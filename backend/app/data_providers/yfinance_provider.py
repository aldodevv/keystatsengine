"""
Yahoo Finance Data Provider for IDX Emitens (.JK suffix).
Fetches real-time market data, financials, balance sheets, and cash flows with fast fallback and caching.
"""

from typing import Optional, List
import concurrent.futures
import yfinance as yf
from app.data_providers.base import BaseDataProvider
from app.data_providers.mock_provider import MockDataProvider
from app.models.keystats import RawKeyStats, FinancialPeriod, BankSpecificMetrics
from app.models.chart import CandleDataPoint


class YFinanceProvider(BaseDataProvider):
    def __init__(self, fallback_to_mock: bool = True):
        self.fallback_provider = MockDataProvider() if fallback_to_mock else None
        self._cache = {}

    def get_keystats(self, ticker: str, override_price: Optional[float] = None, force_live: bool = True) -> Optional[RawKeyStats]:
        clean_ticker = ticker.upper().replace(".JK", "").strip()
        
        # Check cache if not forcing live fetch and no price override
        if not force_live and not override_price and clean_ticker in self._cache:
            return self._cache[clean_ticker]
            
        # 1. Primary: ALWAYS fetch live real market data from Yahoo Finance (.JK)
        try:
            raw = self._fetch_live_yf(clean_ticker)
            if raw:
                if override_price and override_price > 0:
                    raw.current_price = float(override_price)
                    raw.market_cap = float(override_price * raw.shares_outstanding)
                self._cache[clean_ticker] = raw
                return raw
        except Exception as e:
            pass

        # 2. Fallback only if live fetch failed (e.g. offline)
        if self.fallback_provider:
            base_data = self.fallback_provider.get_keystats(clean_ticker)
            if base_data:
                data = base_data.model_copy(deep=True)
                if override_price and override_price > 0:
                    data.current_price = float(override_price)
                    data.market_cap = float(override_price * data.shares_outstanding)
                return data

        return None

    def _fetch_live_yf(self, clean_ticker: str) -> Optional[RawKeyStats]:
        import yfinance as yf
        yf_ticker_str = f"{clean_ticker}.JK"
        stock = yf.Ticker(yf_ticker_str)
        fast_info = getattr(stock, "fast_info", None)
        
        current_price = None
        if fast_info:
            current_price = getattr(fast_info, "last_price", None) or getattr(fast_info, "previous_close", None)
            
        info = {}
        try:
            info = stock.info or {}
        except Exception:
            pass

        if not current_price:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            
        if not current_price:
            return None
            
        shares = (fast_info.shares if fast_info and hasattr(fast_info, "shares") else None) or info.get("sharesOutstanding") or 1.0
        market_cap = (fast_info.market_cap if fast_info and hasattr(fast_info, "market_cap") else None) or info.get("marketCap") or (current_price * shares)
        
        # Detect reporting currency (e.g. USD for ADMR, ADRO, MEDC, ITMG vs IDR)
        financial_curr = info.get("financialCurrency") or (fast_info.currency if fast_info and hasattr(fast_info, "currency") else None) or "IDR"
        fx_multiplier = 1.0
        if str(financial_curr).upper() == "USD":
            fx_multiplier = 16400.0

        # Build periods from live statements
        income_stmt = stock.income_stmt if hasattr(stock, "income_stmt") and stock.income_stmt is not None and not stock.income_stmt.empty else stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        q_inc = getattr(stock, "quarterly_income_stmt", None)
        if q_inc is None or q_inc.empty:
            q_inc = getattr(stock, "quarterly_financials", None)
        q_bal = getattr(stock, "quarterly_balance_sheet", None)
        q_cf = getattr(stock, "quarterly_cashflow", None)
        
        # Check if raw revenue is in USD or thousands (e.g. Market Cap > 1T IDR but Revenue < 10B)
        if income_stmt is not None and not income_stmt.empty:
            try:
                first_rev = float(income_stmt.iloc[0, 0]) if len(income_stmt.columns) > 0 else 0.0
                if market_cap > 1_000_000_000_000 and 0 < first_rev < 10_000_000_000:
                    fx_multiplier = 16400.0
            except Exception:
                pass
        
        current_period = self._extract_period(income_stmt, balance_sheet, cashflow, col_idx=0, shares=shares, fx_multiplier=fx_multiplier)
        previous_period = self._extract_period(income_stmt, balance_sheet, cashflow, col_idx=1, shares=shares, fx_multiplier=fx_multiplier)
        
        historical_periods = []
        num_cols = len(income_stmt.columns) if income_stmt is not None and not income_stmt.empty else 0
        for col_idx in range(1, min(num_cols, 6)):
            hist_p = self._extract_period(income_stmt, balance_sheet, cashflow, col_idx=col_idx, shares=shares, fx_multiplier=fx_multiplier)
            if hist_p and (hist_p.revenue > 0 or hist_p.net_income > 0):
                historical_periods.append(hist_p)
                
        # Extract dividends
        dps_val = 0.0
        try:
            divs = stock.dividends
            if divs is not None and not divs.empty:
                last_idx = divs.index[-1]
                last_year = getattr(last_idx, "year", 2026)
                recent_divs = divs[divs.index >= f"{last_year-1}-01-01"]
                dps_val = float(recent_divs.sum()) if len(recent_divs) > 0 else float(divs.tail(2).sum())
        except Exception:
            pass

        # Build Stockbit Financial Matrix from real statements
        matrix = self._extract_financial_matrix(
            stock=stock,
            shares=shares,
            current_price=float(current_price),
            fx_multiplier=fx_multiplier,
            curr_period=current_period,
            dps_val=dps_val,
            q_inc=q_inc,
            ann_inc=income_stmt,
            q_bal=q_bal,
            q_cf=q_cf
        )
        
        # Overlay TTM values into current_period if available
        if matrix and matrix.income_statement_ttm:
            if matrix.income_statement_ttm.revenue_ttm > 0:
                current_period.revenue = matrix.income_statement_ttm.revenue_ttm
            if matrix.income_statement_ttm.net_income_ttm != 0:
                current_period.net_income = matrix.income_statement_ttm.net_income_ttm
                current_period.eps = matrix.per_share_metrics.eps_ttm if matrix.per_share_metrics.eps_ttm > 0 else (current_period.net_income / shares)
        
        prev_close_val = getattr(fast_info, "previous_close", None) or info.get("previousClose") or current_price
        price_change_val = round(((current_price - prev_close_val) / prev_close_val * 100), 2) if prev_close_val and prev_close_val > 0 else 0.0

        return RawKeyStats(
            ticker=clean_ticker,
            name=info.get("longName") or info.get("shortName") or f"{clean_ticker} Tbk",
            sector=info.get("sector") or "General",
            industry=info.get("industry") or "General",
            current_price=float(current_price),
            previous_close=float(prev_close_val),
            price_change_pct=price_change_val,
            shares_outstanding=float(shares),
            market_cap=float(market_cap),
            current_period=current_period,
            previous_period=previous_period,
            historical_periods=historical_periods,
            financial_matrix=matrix,
            dps=dps_val,
            beta=float(info.get("beta") or 1.0),
            pe_mean_5y=float(info.get("trailingPE") or 14.0),
            pbv_mean_5y=float(info.get("priceToBook") or 2.0)
        )

    def list_all_tickers(self) -> List[str]:
        if self.fallback_provider:
            return self.fallback_provider.list_all_tickers()
        return ["ADMR", "BBRI", "BBCA", "BMRI", "ASII", "ADRO", "ICBP", "TLKM", "UNTR", "KLBF", "PTBA"]

    def search_tickers(self, query: str) -> List[RawKeyStats]:
        if self.fallback_provider:
            return self.fallback_provider.search_tickers(query)
        return []

    def _extract_period(self, inc, bal, cf, col_idx: int, shares: float, fx_multiplier: float = 1.0) -> FinancialPeriod:
        from datetime import datetime
        year = datetime.now().year - col_idx
        
        if inc is not None and not inc.empty and col_idx < len(inc.columns):
            col_name = inc.columns[col_idx]
            if hasattr(col_name, 'year'):
                year = int(col_name.year)
            elif hasattr(col_name, 'strftime'):
                year = int(col_name.strftime('%Y'))
            else:
                try:
                    year = int(str(col_name)[:4])
                except Exception:
                    pass
        
        def _get_val(df, keys, default=0.0):
            if df is None or df.empty or col_idx >= len(df.columns):
                return default
            for k in keys:
                if k in df.index:
                    try:
                        val = df.loc[k].iloc[col_idx]
                        if val is not None and str(val) != 'nan':
                            return float(val) * fx_multiplier
                    except Exception:
                        pass
            return default

        rev = _get_val(inc, ["Total Revenue", "Operating Revenue", "Revenue"])
        gp = _get_val(inc, ["Gross Profit"])
        op = _get_val(inc, ["Operating Income", "Total Operating Income"])
        ebit = _get_val(inc, ["EBIT", "Normalized EBIT", "Operating Income"])
        ebitda = _get_val(inc, ["EBITDA", "Normalized EBITDA"])
        ni = _get_val(inc, ["Net Income Common Stockholders", "Net Income", "Net Income Continuous Operations"])
        eps = (ni / shares) if shares > 0 else 0.0
        
        assets = _get_val(bal, ["Total Assets"])
        cur_assets = _get_val(bal, ["Current Assets", "Total Current Assets"])
        cash = _get_val(bal, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments", "Cash"])
        inv = _get_val(bal, ["Inventory", "Total Inventories"])
        rec = _get_val(bal, ["Receivables", "Accounts Receivable"])
        liab = _get_val(bal, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
        cur_liab = _get_val(bal, ["Current Liabilities", "Total Current Liabilities"])
        debt = _get_val(bal, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
        st_debt = _get_val(bal, ["Current Debt", "Current Debt And Capital Lease Obligation"])
        lt_debt = _get_val(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
        equity = _get_val(bal, ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"])
        re = _get_val(bal, ["Retained Earnings"])
        
        cfo = _get_val(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
        capex = abs(_get_val(cf, ["Capital Expenditure", "Capital Expenditures"]))
        fcf = _get_val(cf, ["Free Cash Flow"])
        if fcf == 0.0 and cfo != 0.0:
            fcf = cfo - capex
            
        divs = abs(_get_val(cf, ["Cash Dividends Paid", "Common Stock Dividend Paid"]))
        
        return FinancialPeriod(
            year=year,
            revenue=rev,
            gross_profit=gp if gp > 0 else rev * 0.4,
            operating_profit=op if op > 0 else rev * 0.2,
            ebit=ebit if ebit > 0 else op,
            ebitda=ebitda if ebitda > 0 else op * 1.15,
            net_income=ni,
            eps=eps,
            total_assets=assets,
            current_assets=cur_assets,
            cash_and_equivalents=cash,
            inventory=inv,
            receivables=rec,
            total_liabilities=liab,
            current_liabilities=cur_liab,
            total_debt=debt,
            short_term_debt=st_debt,
            long_term_debt=lt_debt,
            total_equity=equity,
            retained_earnings=re,
            cfo=cfo,
            capex=capex,
            fcf=fcf,
            dividends_paid=divs,
            shares_outstanding=shares
        )

    def _extract_financial_matrix(
        self,
        stock,
        shares: float,
        current_price: float,
        fx_multiplier: float,
        curr_period: FinancialPeriod,
        dps_val: float = 0.0,
        q_inc=None,
        ann_inc=None,
        q_bal=None,
        q_cf=None
    ):
        from app.models.financial_matrix import (
            StockbitFinancialMatrix, QuarterlyDataPoint,
            IncomeStatementTTM, BalanceSheetQuarter, PerShareFinancials
        )
        
        years = [2026, 2025, 2024, 2023, 2022, 2021, 2020]
        net_income_mat = {}
        eps_mat = {}
        rev_mat = {}
        
        # 1. Parse Real Quarterly Income Statements
        q_map = {}  # year -> { q1, q2, q3, q4: { ni, rev, eps } }
        if q_inc is not None and not q_inc.empty:
            for c in q_inc.columns:
                y = c.year
                q_num = (c.month - 1) // 3 + 1
                ni = float(q_inc[c].get("Net Income Common Stockholders", q_inc[c].get("Net Income", 0)) or 0) * fx_multiplier
                rev = float(q_inc[c].get("Total Revenue", q_inc[c].get("Operating Revenue", 0)) or 0) * fx_multiplier
                eps = ni / shares if shares > 0 else 0.0
                if y not in q_map:
                    q_map[y] = {}
                q_map[y][f"q{q_num}"] = {"ni": ni, "rev": rev, "eps": eps}
                
        # 2. Parse Real Annual Income Statements
        ann_map = {}  # year -> { ni, rev, eps }
        if ann_inc is not None and not ann_inc.empty:
            for c in ann_inc.columns:
                y = c.year
                ni = float(ann_inc[c].get("Net Income Common Stockholders", ann_inc[c].get("Net Income", 0)) or 0) * fx_multiplier
                rev = float(ann_inc[c].get("Total Revenue", ann_inc[c].get("Operating Revenue", 0)) or 0) * fx_multiplier
                eps = ni / shares if shares > 0 else 0.0
                ann_map[y] = {"ni": ni, "rev": rev, "eps": eps}

        # 3. Parse Dividends
        div_map = {}
        try:
            divs = getattr(stock, "dividends", None)
            if divs is not None and not divs.empty:
                for d_date, d_amount in divs.items():
                    y = getattr(d_date, "year", None)
                    if not y:
                        try:
                            y = int(str(d_date)[:4])
                        except Exception:
                            y = None
                    if y:
                        div_map[y] = div_map.get(y, 0.0) + float(d_amount)
        except Exception:
            pass

        # Calculate TTM (sum of latest 4 quarters or latest active period)
        ttm_ni = 0.0
        ttm_rev = 0.0
        ttm_count = 0
        if q_inc is not None and not q_inc.empty:
            for c in q_inc.columns[:4]:
                ttm_ni += float(q_inc[c].get("Net Income Common Stockholders", q_inc[c].get("Net Income", 0)) or 0) * fx_multiplier
                ttm_rev += float(q_inc[c].get("Total Revenue", q_inc[c].get("Operating Revenue", 0)) or 0) * fx_multiplier
                ttm_count += 1
        
        if ttm_count < 4 or ttm_ni == 0:
            ttm_ni = curr_period.net_income
            ttm_rev = curr_period.revenue

        ttm_eps = round(ttm_ni / shares, 2) if shares > 0 else 0.0

        for y in years:
            y_q = q_map.get(y, {})
            y_ann = ann_map.get(y, {})
            
            # EPS
            q1_eps = y_q.get("q1", {}).get("eps")
            q2_eps = y_q.get("q2", {}).get("eps")
            q3_eps = y_q.get("q3", {}).get("eps")
            q4_eps = y_q.get("q4", {}).get("eps")
            
            ann_eps = y_ann.get("eps")
            if ann_eps is None and y_q:
                # Sum available quarters or project
                ann_eps = sum(v["eps"] for v in y_q.values())
            
            annualised_eps = round(q1_eps * 4.0, 2) if (y == 2026 and q1_eps is not None) else (round(ann_eps, 2) if ann_eps is not None else None)
            ttm_year_eps = ttm_eps if y == 2026 else (round(ann_eps, 2) if ann_eps is not None else None)
            
            # Dividend and Payout
            y_dps = div_map.get(y, dps_val if y == 2026 else None)
            payout = round((y_dps / (ttm_year_eps or 1.0) * 100), 2) if (y_dps and ttm_year_eps and ttm_year_eps > 0) else None
            div_yield = round((y_dps / current_price * 100), 2) if (y_dps and current_price > 0) else None
            
            eps_mat[str(y)] = QuarterlyDataPoint(
                q1=round(q1_eps, 2) if q1_eps is not None else None,
                q2=round(q2_eps, 2) if q2_eps is not None else None,
                q3=round(q3_eps, 2) if q3_eps is not None else None,
                q4=round(q4_eps, 2) if q4_eps is not None else None,
                annualised=annualised_eps,
                ttm=ttm_year_eps,
                dividend_ttm=round(y_dps, 2) if y_dps is not None else None,
                payout_ratio_pct=payout,
                dividend_yield_pct=div_yield
            )
            
            # Revenue
            q1_rev = y_q.get("q1", {}).get("rev")
            q2_rev = y_q.get("q2", {}).get("rev")
            q3_rev = y_q.get("q3", {}).get("rev")
            q4_rev = y_q.get("q4", {}).get("rev")
            ann_rev = y_ann.get("rev")
            if ann_rev is None and y_q:
                ann_rev = sum(v["rev"] for v in y_q.values())
            
            annualised_rev = round(q1_rev * 4.0, 0) if (y == 2026 and q1_rev is not None) else (round(ann_rev, 0) if ann_rev is not None else None)
            ttm_year_rev = round(ttm_rev, 0) if y == 2026 else (round(ann_rev, 0) if ann_rev is not None else None)
            
            rev_mat[str(y)] = QuarterlyDataPoint(
                q1=round(q1_rev, 0) if q1_rev is not None else None,
                q2=round(q2_rev, 0) if q2_rev is not None else None,
                q3=round(q3_rev, 0) if q3_rev is not None else None,
                q4=round(q4_rev, 0) if q4_rev is not None else None,
                annualised=annualised_rev,
                ttm=ttm_year_rev,
                dividend_ttm=round(y_dps, 2) if y_dps is not None else None,
                payout_ratio_pct=payout,
                dividend_yield_pct=div_yield
            )
            
            # Net Income
            q1_ni = y_q.get("q1", {}).get("ni")
            q2_ni = y_q.get("q2", {}).get("ni")
            q3_ni = y_q.get("q3", {}).get("ni")
            q4_ni = y_q.get("q4", {}).get("ni")
            ann_ni = y_ann.get("ni")
            if ann_ni is None and y_q:
                ann_ni = sum(v["ni"] for v in y_q.values())
                
            annualised_ni = round(q1_ni * 4.0, 0) if (y == 2026 and q1_ni is not None) else (round(ann_ni, 0) if ann_ni is not None else None)
            ttm_year_ni = round(ttm_ni, 0) if y == 2026 else (round(ann_ni, 0) if ann_ni is not None else None)
            
            net_income_mat[str(y)] = QuarterlyDataPoint(
                q1=round(q1_ni, 0) if q1_ni is not None else None,
                q2=round(q2_ni, 0) if q2_ni is not None else None,
                q3=round(q3_ni, 0) if q3_ni is not None else None,
                q4=round(q4_ni, 0) if q4_ni is not None else None,
                annualised=annualised_ni,
                ttm=ttm_year_ni,
                dividend_ttm=round(y_dps, 2) if y_dps is not None else None,
                payout_ratio_pct=payout,
                dividend_yield_pct=div_yield
            )

        # Balance sheet metrics
        def _get_bs_val(keys, default=0.0):
            for df in [q_bal, stock.balance_sheet]:
                if df is not None and not df.empty:
                    for k in keys:
                        if k in df.index:
                            try:
                                val = df.loc[k].iloc[0]
                                if val is not None and str(val) != 'nan':
                                    return float(val) * fx_multiplier
                            except Exception:
                                pass
            return default

        cash_val = _get_bs_val(["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments", "Cash"], curr_period.cash_and_equivalents)
        assets_val = _get_bs_val(["Total Assets"], curr_period.total_assets)
        liab_val = _get_bs_val(["Total Liabilities Net Minority Interest", "Total Liabilities"], curr_period.total_liabilities)
        equity_val = _get_bs_val(["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"], curr_period.total_equity)
        cur_assets_val = _get_bs_val(["Current Assets", "Total Current Assets"], curr_period.current_assets)
        cur_liab_val = _get_bs_val(["Current Liabilities", "Total Current Liabilities"], curr_period.current_liabilities)
        debt_val = _get_bs_val(["Total Debt", "Long Term Debt And Capital Lease Obligation"], curr_period.total_debt)
        lt_debt_val = _get_bs_val(["Long Term Debt"], curr_period.long_term_debt)
        st_debt_val = _get_bs_val(["Current Debt"], curr_period.short_term_debt)
        
        # Cash flow metrics
        def _get_cf_val(keys, default=0.0):
            for df in [q_cf, stock.cashflow]:
                if df is not None and not df.empty:
                    for k in keys:
                        if k in df.index:
                            try:
                                val = df.loc[k].iloc[0]
                                if val is not None and str(val) != 'nan':
                                    return float(val) * fx_multiplier
                            except Exception:
                                pass
            return default
            
        cfo_val = _get_cf_val(["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"], curr_period.cfo)
        fcf_val = _get_cf_val(["Free Cash Flow"], curr_period.fcf)

        return StockbitFinancialMatrix(
            years=years,
            currency="IDR",
            net_income_matrix=net_income_mat,
            eps_matrix=eps_mat,
            revenue_matrix=rev_mat,
            income_statement_ttm=IncomeStatementTTM(
                revenue_ttm=ttm_rev,
                gross_profit_ttm=curr_period.gross_profit if curr_period.gross_profit > 0 else ttm_rev * 0.4,
                ebitda_ttm=curr_period.ebitda if curr_period.ebitda > 0 else ttm_rev * 0.3,
                net_income_ttm=ttm_ni
            ),
            balance_sheet_quarter=BalanceSheetQuarter(
                cash=cash_val,
                total_assets=assets_val,
                total_liabilities=liab_val,
                working_capital=cur_assets_val - cur_liab_val,
                common_equity=equity_val,
                long_term_debt=lt_debt_val,
                short_term_debt=st_debt_val,
                total_debt=debt_val,
                net_debt=max(0.0, debt_val - cash_val),
                total_equity=equity_val
            ),
            per_share_metrics=PerShareFinancials(
                eps_ttm=ttm_eps,
                eps_annualised=round(ttm_eps * 1.06, 2),
                revenue_per_share_ttm=round(ttm_rev / shares, 2) if shares > 0 else 0.0,
                cash_per_share=round(cash_val / shares, 2) if shares > 0 else 0.0,
                book_value_per_share=round(equity_val / shares, 2) if shares > 0 else 0.0,
                fcf_per_share_ttm=round(fcf_val / shares, 2) if shares > 0 else 0.0
            )
        )

    def get_historical_ohlcv(self, ticker: str, timeframe: str = "1y") -> List[CandleDataPoint]:
        """Fetches live daily OHLCV candles from Yahoo Finance with mock fallback."""
        clean_ticker = ticker.upper().strip()
        formatted = f"{clean_ticker}.JK" if not clean_ticker.endswith(".JK") else clean_ticker
        
        # Valid yfinance period mapping
        period_map = {
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "5y": "5y"
        }
        period = period_map.get(timeframe.lower(), "1y")
        interval = "1d" if period != "5y" else "1wk"
        
        try:
            stock = yf.Ticker(formatted)
            df = stock.history(period=period, interval=interval)
            
            if df is not None and not df.empty and len(df) > 5:
                candles: List[CandleDataPoint] = []
                for idx, row in df.iterrows():
                    date_str = str(idx)[:10]
                    try:
                        val_open = row['Open'] if 'Open' in row else 0.0
                        val_high = row['High'] if 'High' in row else 0.0
                        val_low = row['Low'] if 'Low' in row else 0.0
                        val_close = row['Close'] if 'Close' in row else 0.0
                        val_vol = row['Volume'] if 'Volume' in row else 0
                        
                        o = float(val_open) if val_open is not None else 0.0
                        h = float(val_high) if val_high is not None else 0.0
                        l = float(val_low) if val_low is not None else 0.0
                        c = float(val_close) if val_close is not None else 0.0
                        v = int(float(val_vol)) if val_vol is not None else 0
                    except Exception:
                        continue
                    
                    if o > 0 and c > 0:
                        candles.append(CandleDataPoint(
                            time=date_str,
                            open=round(o, 2),
                            high=round(h, 2),
                            low=round(l, 2),
                            close=round(c, 2),
                            volume=v
                        ))
                if len(candles) >= 5:
                    return candles
        except Exception:
            pass
            
        # Fallback to mock provider
        if self.fallback_provider:
            return self.fallback_provider.get_historical_ohlcv(clean_ticker.replace(".JK", ""), timeframe)
        return []
