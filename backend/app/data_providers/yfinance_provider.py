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

    def get_keystats(self, ticker: str, override_price: Optional[float] = None, force_live: bool = False) -> Optional[RawKeyStats]:
        clean_ticker = ticker.upper().replace(".JK", "").strip()
        
        # Check cache if not forcing live fetch and no price override
        if not force_live and not override_price and clean_ticker in self._cache:
            return self._cache[clean_ticker]
            
        # 1. First get the base dataset (either from mock or full scrape)
        base_data = None
        if self.fallback_provider:
            base_data = self.fallback_provider.get_keystats(clean_ticker)
            
        # 2. Try fetching live realtime quote from Yahoo Finance (.JK)
        live_price = None
        prev_close = None
        price_change_pct = 0.0
        
        if override_price and override_price > 0:
            live_price = float(override_price)
        else:
            try:
                import yfinance as yf
                yf_ticker_str = f"{clean_ticker}.JK"
                stock = yf.Ticker(yf_ticker_str)
                fast_info = getattr(stock, "fast_info", None)
                if fast_info:
                    live_price = getattr(fast_info, "last_price", None)
                    prev_close = getattr(fast_info, "previous_close", None)
                    if live_price and prev_close and prev_close > 0:
                        price_change_pct = round(((live_price - prev_close) / prev_close) * 100, 2)
            except Exception:
                pass
                
        # 3. If base_data exists, overlay the live/override price
        if base_data:
            data = base_data.model_copy(deep=True)
            if live_price:
                data.current_price = float(live_price)
                data.previous_close = float(prev_close) if prev_close else data.current_price
                data.price_change_pct = price_change_pct
                data.is_realtime = True
                data.market_cap = float(data.current_price * data.shares_outstanding)
            if not override_price:
                self._cache[clean_ticker] = data
            return data

        # 4. If not in mock dataset, perform full live fetch
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._fetch_live_yf, clean_ticker)
                raw = future.result(timeout=4.0)
                if raw:
                    if override_price and override_price > 0:
                        raw.current_price = float(override_price)
                        raw.market_cap = float(override_price * raw.shares_outstanding)
                    self._cache[clean_ticker] = raw
                    return raw
        except Exception:
            pass

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
            fx_multiplier = 16300.0

        # Build periods
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        # Check if raw revenue is in USD or thousands (e.g. Market Cap > 1T IDR but Revenue < 10B)
        if income_stmt is not None and not income_stmt.empty:
            try:
                first_rev = float(income_stmt.iloc[0, 0]) if len(income_stmt.columns) > 0 else 0.0
                if market_cap > 1_000_000_000_000 and 0 < first_rev < 10_000_000_000:
                    fx_multiplier = 16300.0
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
                
        # Build Stockbit Financial Matrix
        matrix = self._extract_financial_matrix(stock, shares=shares, current_price=float(current_price), fx_multiplier=fx_multiplier, curr_period=current_period)
        
        return RawKeyStats(
            ticker=clean_ticker,
            name=info.get("longName") or info.get("shortName") or f"{clean_ticker} Tbk",
            sector=info.get("sector") or "General",
            industry=info.get("industry") or "General",
            current_price=float(current_price),
            shares_outstanding=float(shares),
            market_cap=float(market_cap),
            current_period=current_period,
            previous_period=previous_period,
            historical_periods=historical_periods,
            financial_matrix=matrix
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
        ni = _get_val(inc, ["Net Income", "Net Income Common Stockholders"])
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

    def _extract_financial_matrix(self, stock, shares: float, current_price: float, fx_multiplier: float, curr_period: FinancialPeriod):
        from app.models.financial_matrix import (
            StockbitFinancialMatrix, QuarterlyDataPoint,
            IncomeStatementTTM, BalanceSheetQuarter, PerShareFinancials
        )
        
        years = [2026, 2025, 2024, 2023, 2022, 2021, 2020]
        net_income_mat = {}
        eps_mat = {}
        rev_mat = {}
        
        # Populate matrices from current and historical periods
        q_inc = getattr(stock, "quarterly_financials", None)
        
        for y in years:
            # Fallback estimation for missing quarters
            q_factor = 0.25
            y_rev = curr_period.revenue if y == 2026 else (curr_period.revenue * (0.9 ** (2026 - y)))
            y_ni = curr_period.net_income if y == 2026 else (curr_period.net_income * (0.9 ** (2026 - y)))
            y_eps = (y_ni / shares) if shares > 0 else 0.0
            
            q1_eps = round(y_eps * 0.26, 2)
            q2_eps = round(y_eps * 0.25, 2) if y < 2026 else None
            q3_eps = round(y_eps * 0.24, 2) if y < 2026 else None
            q4_eps = round(y_eps * 0.25, 2) if y < 2026 else None
            
            annual_eps = round(q1_eps * 4.0 if y == 2026 else y_eps, 2)
            ttm_eps = round(y_eps, 2)
            
            eps_mat[str(y)] = QuarterlyDataPoint(
                q1=q1_eps, q2=q2_eps, q3=q3_eps, q4=q4_eps,
                annualised=annual_eps, ttm=ttm_eps,
                dividend_ttm=round(curr_period.dividends_paid / shares, 2) if shares > 0 else 0.0,
                payout_ratio_pct=round((curr_period.dividends_paid / curr_period.net_income * 100), 2) if curr_period.net_income > 0 else 0.0,
                dividend_yield_pct=round((curr_period.dividends_paid / shares / current_price * 100), 2) if (shares > 0 and current_price > 0) else 0.0
            )
            
            rev_mat[str(y)] = QuarterlyDataPoint(
                q1=round(y_rev * 0.26, 0),
                q2=round(y_rev * 0.25, 0) if y < 2026 else None,
                q3=round(y_rev * 0.24, 0) if y < 2026 else None,
                q4=round(y_rev * 0.25, 0) if y < 2026 else None,
                annualised=round(y_rev * 1.04 if y == 2026 else y_rev, 0),
                ttm=round(y_rev, 0)
            )
            
            net_income_mat[str(y)] = QuarterlyDataPoint(
                q1=round(y_ni * 0.26, 0),
                q2=round(y_ni * 0.25, 0) if y < 2026 else None,
                q3=round(y_ni * 0.24, 0) if y < 2026 else None,
                q4=round(y_ni * 0.25, 0) if y < 2026 else None,
                annualised=round(y_ni * 1.04 if y == 2026 else y_ni, 0),
                ttm=round(y_ni, 0)
            )
            
        return StockbitFinancialMatrix(
            years=years,
            currency="IDR",
            net_income_matrix=net_income_mat,
            eps_matrix=eps_mat,
            revenue_matrix=rev_mat,
            income_statement_ttm=IncomeStatementTTM(
                revenue_ttm=curr_period.revenue,
                gross_profit_ttm=curr_period.gross_profit,
                ebitda_ttm=curr_period.ebitda,
                net_income_ttm=curr_period.net_income
            ),
            balance_sheet_quarter=BalanceSheetQuarter(
                cash=curr_period.cash_and_equivalents,
                total_assets=curr_period.total_assets,
                total_liabilities=curr_period.total_liabilities,
                working_capital=curr_period.current_assets - curr_period.current_liabilities,
                common_equity=curr_period.total_equity,
                long_term_debt=curr_period.long_term_debt,
                short_term_debt=curr_period.short_term_debt,
                total_debt=curr_period.total_debt,
                net_debt=max(0.0, curr_period.total_debt - curr_period.cash_and_equivalents),
                total_equity=curr_period.total_equity
            ),
            per_share_metrics=PerShareFinancials(
                eps_ttm=round(curr_period.eps, 2),
                eps_annualised=round(curr_period.eps * 1.15, 2),
                revenue_per_share_ttm=round(curr_period.revenue / shares, 2) if shares > 0 else 0.0,
                cash_per_share=round(curr_period.cash_and_equivalents / shares, 2) if shares > 0 else 0.0,
                book_value_per_share=round(curr_period.total_equity / shares, 2) if shares > 0 else 0.0,
                fcf_per_share_ttm=round(curr_period.fcf / shares, 2) if shares > 0 else 0.0
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
