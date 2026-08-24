"""
FastAPI Endpoints for Quantitative Screener and Presets.
"""

from fastapi import APIRouter
from typing import List, Dict
from app.services.emiten_service import EmitenService
from app.services.screener_service import ScreenerService
from app.models.screener import ScreenerCriteria, ScreenerResponse, ScreenerPreset

router = APIRouter(prefix="/screener", tags=["Quantitative Screener"])
emiten_service = EmitenService()
screener_service = ScreenerService(emiten_service)


@router.post("/run", response_model=ScreenerResponse)
def run_screener(criteria: ScreenerCriteria):
    """Runs the multi-factor screener against all emitens with customizable criteria."""
    return screener_service.run_screener(criteria)


@router.get("/presets")
def get_presets() -> List[Dict[str, str]]:
    """Returns available screener preset strategies with their rationale."""
    return [
        {
            "id": ScreenerPreset.BUFFETT_MOAT.value,
            "name": "Buffett Quality Moat",
            "description": "High ROE (>14%), low debt (DER < 1.0x), strong Piotroski F-Score (>=6), and positive Free Cash Flow."
        },
        {
            "id": ScreenerPreset.DIVIDEND_CASH_COW.value,
            "name": "Dividend Cash Cow",
            "description": "High dividend yield (>4.5%), safe payout ratio (<80%), safe Altman Z-Score, and positive FCF."
        },
        {
            "id": ScreenerPreset.GARP.value,
            "name": "GARP (Growth At Reasonable Price)",
            "description": "Attractive PEG ratio (<1.2x), solid EPS growth (>8%), and robust ROE (>10%)."
        },
        {
            "id": ScreenerPreset.DEEP_VALUE.value,
            "name": "Deep Value & Turnaround",
            "description": "Low PBV (<1.5x), low PER (<12x), upside potential (>15%), with no bankruptcy risk."
        },
        {
            "id": ScreenerPreset.MOMENTUM_QUALITY.value,
            "name": "Momentum & Quality Growth",
            "description": "Double-digit EPS growth (>10%), top revenue expansion, and high operating efficiency."
        }
    ]
