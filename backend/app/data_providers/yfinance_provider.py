"""
Yahoo Finance Data Provider (DEPRECATED):
Deprecated for IDX instruments (.JK) due to high rates of silently dropped Q4 reports and unadjusted pricing.
Replaced with InstitutionalDataProvider (EODHD institutional data feed).
"""

from typing import Optional, List
from app.data_providers.base import BaseDataProvider
from app.data_providers.institutional_provider import InstitutionalDataProvider
from app.models.keystats import RawKeyStats
from app.models.chart import CandleDataPoint


class YFinanceProvider(BaseDataProvider):
    """
    Deprecated Yahoo Finance adapter. Automatically routes to InstitutionalDataProvider.
    """
    def __init__(self, fallback_to_mock: bool = True):
        self._provider = InstitutionalDataProvider()

    def get_keystats(
        self,
        ticker: str,
        override_price: Optional[float] = None,
        force_live: bool = False
    ) -> Optional[RawKeyStats]:
        return self._provider.get_keystats(ticker, override_price=override_price, force_live=force_live)

    def list_all_tickers(self) -> List[str]:
        return self._provider.list_all_tickers()

    def search_tickers(self, query: str) -> List[RawKeyStats]:
        return self._provider.search_tickers(query)

    def get_historical_ohlcv(self, ticker: str, timeframe: str = "1y") -> List[CandleDataPoint]:
        return self._provider.get_historical_ohlcv(ticker, timeframe=timeframe)

    def get_bulk_market_data(self):
        return self._provider.get_bulk_market_data()
