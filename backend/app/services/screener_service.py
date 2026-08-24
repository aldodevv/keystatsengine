"""
Screener Service: Multi-emiten filtering, custom ratio filtering, and preset strategies.
"""

from typing import List, Optional
from app.services.emiten_service import EmitenService
from app.models.screener import ScreenerCriteria, ScreenerPreset, ScreenerResponse, EmitenSummaryItem
from app.models.score import EmitenAnalysisReport


class ScreenerService:
    def __init__(self, emiten_service: EmitenService):
        self.emiten_service = emiten_service

    def run_screener(self, criteria: Optional[ScreenerCriteria] = None) -> ScreenerResponse:
        criteria = criteria or ScreenerCriteria()
        
        # If preset is selected, apply preset thresholds
        if criteria.preset and criteria.preset != ScreenerPreset.CUSTOM:
            criteria = self._apply_preset(criteria.preset, criteria)
            
        all_tickers = self.emiten_service.list_all_available_tickers()
        matched: List[EmitenSummaryItem] = []
        
        for t in all_tickers:
            report = self.emiten_service.analyze_single_emiten(t)
            if not report:
                continue
                
            if self._matches_criteria(report, criteria):
                item = EmitenSummaryItem(
                    ticker=report.ticker,
                    name=report.name,
                    sector=report.sector,
                    current_price=report.current_price,
                    market_cap=report.market_cap,
                    per=report.valuation.per,
                    pbv=report.valuation.pbv,
                    roe=report.profitability.roe,
                    der=report.solvency.der,
                    piotroski_f_score=report.quality.piotroski_f_score,
                    altman_z_score=report.solvency.altman_z_score,
                    dividend_yield=report.cash_flow_dividend.dividend_yield,
                    composite_score=report.composite_score,
                    grade=report.grade,
                    verdict=report.verdict.value,
                    upside_pct=report.valuation.upside_downside_pct
                )
                matched.append(item)
                
        # Sort by composite score descending by default
        matched.sort(key=lambda x: x.composite_score, reverse=True)
        
        return ScreenerResponse(
            total_matched=len(matched),
            results=matched,
            applied_preset=criteria.preset.value if criteria.preset else None
        )

    def _matches_criteria(self, rep: EmitenAnalysisReport, c: ScreenerCriteria) -> bool:
        # Sectors
        if c.sectors and rep.sector not in c.sectors:
            return False
            
        # Market Cap
        if c.min_market_cap and rep.market_cap < c.min_market_cap:
            return False
        if c.max_market_cap and rep.market_cap > c.max_market_cap:
            return False
            
        # Valuation
        if c.min_pe and rep.valuation.per < c.min_pe:
            return False
        if c.max_pe and rep.valuation.per > c.max_pe:
            return False
        if c.min_pbv and rep.valuation.pbv < c.min_pbv:
            return False
        if c.max_pbv and rep.valuation.pbv > c.max_pbv:
            return False
        if c.max_peg and rep.valuation.peg_ratio is not None and rep.valuation.peg_ratio > c.max_peg:
            return False
        if c.min_upside_pct and rep.valuation.upside_downside_pct < c.min_upside_pct:
            return False
            
        # Profitability
        if c.min_roe and rep.profitability.roe < c.min_roe:
            return False
        if c.min_npm and rep.profitability.npm < c.min_npm:
            return False
        if c.min_roic and rep.profitability.roic < c.min_roic:
            return False
            
        # Solvency & Quality
        if c.max_der and rep.solvency.der > c.max_der:
            return False
        if c.min_altman_z and rep.solvency.altman_z_score < c.min_altman_z:
            return False
        if c.min_piotroski_f and rep.quality.piotroski_f_score < c.min_piotroski_f:
            return False
        if c.min_current_ratio and rep.liquidity.current_ratio < c.min_current_ratio:
            return False
            
        # Dividend & Cash Flow
        if c.min_dividend_yield and rep.cash_flow_dividend.dividend_yield < c.min_dividend_yield:
            return False
        if c.max_dpr and rep.cash_flow_dividend.dpr > c.max_dpr:
            return False
        if c.must_have_positive_fcf and rep.cash_flow_dividend.fcf <= 0:
            return False
            
        # Growth
        if c.min_revenue_growth and rep.growth.revenue_growth_yoy < c.min_revenue_growth:
            return False
        if c.min_eps_growth and rep.growth.eps_growth_yoy < c.min_eps_growth:
            return False
            
        # Composite Score
        if c.min_composite_score and rep.composite_score < c.min_composite_score:
            return False
            
        return True

    def _apply_preset(self, preset: ScreenerPreset, existing: ScreenerCriteria) -> ScreenerCriteria:
        c = existing.model_copy()
        
        if preset == ScreenerPreset.BUFFETT_MOAT:
            c.min_roe = 14.0
            c.max_der = 1.0
            c.min_piotroski_f = 6
            c.must_have_positive_fcf = True
            c.min_composite_score = 65.0
            
        elif preset == ScreenerPreset.DIVIDEND_CASH_COW:
            c.min_dividend_yield = 4.5
            c.max_dpr = 80.0
            c.min_altman_z = 1.8
            c.must_have_positive_fcf = True
            
        elif preset == ScreenerPreset.GARP:
            c.max_peg = 1.2
            c.min_eps_growth = 8.0
            c.min_roe = 10.0
            c.min_upside_pct = 5.0
            
        elif preset == ScreenerPreset.DEEP_VALUE:
            c.max_pbv = 1.5
            c.max_pe = 12.0
            c.min_upside_pct = 15.0
            c.min_altman_z = 1.5
            
        elif preset == ScreenerPreset.MOMENTUM_QUALITY:
            c.min_eps_growth = 10.0
            c.min_revenue_growth = 6.0
            c.min_piotroski_f = 6
            c.min_composite_score = 60.0
            
        return c
