"""
Emiten Service: Coordinates data fetching and analytical scoring for single emitens.
Uses InstitutionalDataProvider as primary data source.
"""

from typing import Optional, List
from app.data_providers.base import BaseDataProvider
from app.data_providers.institutional_provider import InstitutionalDataProvider
from app.engines.scoring_engine import ScoringEngine
from app.models.score import EmitenAnalysisReport
from app.models.keystats import RawKeyStats
from app.models.ownership import OwnershipBreakdown
from app.services.ksei_service import KSEIStatisticsService


class EmitenService:
    def __init__(self, provider: Optional[BaseDataProvider] = None):
        self.provider = provider or InstitutionalDataProvider()

    def analyze_single_emiten(
        self,
        ticker: str,
        override_price: Optional[float] = None,
        force_live: bool = False
    ) -> Optional[EmitenAnalysisReport]:
        raw = self.provider.get_keystats(ticker, override_price=override_price, force_live=force_live)
        if not raw:
            return None
        report = ScoringEngine.analyze_emiten(raw)

        # Attach real shareholder/ownership composition (best-effort; never blocks analysis).
        try:
            report.ownership = self.get_shareholders(ticker)
        except Exception:
            report.ownership = None

        return report

    def search_emitens(self, query: str) -> List[RawKeyStats]:
        return self.provider.search_tickers(query)

    def list_all_available_tickers(self) -> List[str]:
        return self.provider.list_all_tickers()

    def get_shareholders(self, ticker: str) -> Optional[OwnershipBreakdown]:
        """
        Retrieves real shareholder / stakeholder ownership composition for a ticker,
        enriched (when configured) with KSEI SID retail-participation statistics.
        Returns None when no real ownership data is available.
        """
        ownership = self.provider.get_shareholders(ticker)
        if ownership is None:
            return None

        sid = KSEIStatisticsService.get_market_sid()
        if sid is not None:
            ownership.sid_statistics = sid
        return ownership
