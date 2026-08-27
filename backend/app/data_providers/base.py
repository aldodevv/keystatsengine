"""
Base Data Provider Interface for IDX Keystats and Financial Statements.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.keystats import RawKeyStats
from app.models.chart import CandleDataPoint


class BaseDataProvider(ABC):
    @abstractmethod
    def get_keystats(
        self,
        ticker: str,
        override_price: Optional[float] = None,
        force_live: bool = False
    ) -> Optional[RawKeyStats]:
        """Fetches raw keystats and financial statements for a given ticker."""
        pass
        
    @abstractmethod
    def list_all_tickers(self) -> List[str]:
        """Returns all available IDX tickers."""
        pass
        
    @abstractmethod
    def search_tickers(self, query: str) -> List[RawKeyStats]:
        """Searches tickers by code or name."""
        pass

    @abstractmethod
    def get_historical_ohlcv(self, ticker: str, timeframe: str = "1y") -> List[CandleDataPoint]:
        """Fetches historical daily OHLCV candlestick data."""
        pass

