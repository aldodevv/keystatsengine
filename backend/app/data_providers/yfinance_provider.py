"""
Yahoo Finance Data Provider for IDX Emitens (.JK suffix).
Fetches real-time market data, financials, balance sheets, and cash flows with fast fallback and caching.
"""

from typing import Optional, List
import concurrent.futures
from app.data_providers.base import BaseDataProvider
from app.data_providers.mock_provider import MockDataProvider
from app.models.keystats import RawKeyStats, FinancialPeriod, BankSpecificMetrics


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
            
        if not current_price:
            info = stock.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            
        if not current_price:
            return None
            
        shares = (fast_info.shares if fast_info and hasattr(fast_info, "shares") else None) or 1.0
        market_cap = (fast_info.market_cap if fast_info and hasattr(fast_info, "market_cap") else None) or (current_price * shares)
        
        # Build period
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        current_period = self._extract_period(income_stmt, balance_sheet, cashflow, col_idx=0, shares=shares)
        previous_period = self._extract_period(income_stmt, balance_sheet, cashflow, col_idx=1, shares=shares)
        
        return RawKeyStats(
            ticker=clean_ticker,
            name=f"{clean_ticker} Tbk",
            sector="General",
            industry="General",
            current_price=float(current_price),
            shares_outstanding=float(shares),
            market_cap=float(market_cap),
            current_period=current_period,
            previous_period=previous_period
        )

    def list_all_tickers(self) -> List[str]:
        if self.fallback_provider:
            return self.fallback_provider.list_all_tickers()
        return ["BBRI", "BBCA", "BMRI", "ASII", "ADRO", "ICBP", "TLKM", "UNTR", "KLBF", "PTBA"]

    def search_tickers(self, query: str) -> List[RawKeyStats]:
        if self.fallback_provider:
            return self.fallback_provider.search_tickers(query)
        return []

    def _extract_period(self, inc, bal, cf, col_idx: int, shares: float) -> FinancialPeriod:
        year = 2024 - col_idx
        
        def _get_val(df, keys, default=0.0):
            if df is None or df.empty or col_idx >= len(df.columns):
                return default
            for k in keys:
                if k in df.index:
                    try:
                        val = df.loc[k].iloc[col_idx]
                        if val is not None and str(val) != 'nan':
                            return float(val)
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
