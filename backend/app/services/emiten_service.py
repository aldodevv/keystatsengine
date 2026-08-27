"""
Emiten Service: Coordinates data fetching and analytical scoring for single emitens.
"""

from typing import Optional, List
from app.data_providers.base import BaseDataProvider
from app.data_providers.yfinance_provider import YFinanceProvider
from app.engines.scoring_engine import ScoringEngine
from app.models.score import EmitenAnalysisReport
from app.models.keystats import RawKeyStats


class EmitenService:
    def __init__(self, provider: Optional[BaseDataProvider] = None):
        self.provider = provider or YFinanceProvider(fallback_to_mock=True)

    def analyze_single_emiten(
        self,
        ticker: str,
        override_price: Optional[float] = None,
        force_live: bool = True
    ) -> Optional[EmitenAnalysisReport]:
        if hasattr(self.provider, "get_keystats"):
            raw = self.provider.get_keystats(ticker, override_price=override_price, force_live=force_live)
        else:
            raw = self.provider.get_keystats(ticker)
            
        if not raw:
            return None
        return ScoringEngine.analyze_emiten(raw)

    def search_emitens(self, query: str) -> List[RawKeyStats]:
        return self.provider.search_tickers(query)

    def list_all_available_tickers(self) -> List[str]:
        return self.provider.list_all_tickers()
