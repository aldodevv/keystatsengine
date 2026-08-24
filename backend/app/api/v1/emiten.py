"""
FastAPI Endpoints for Single Emiten Analysis & Search.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.emiten_service import EmitenService
from app.models.score import EmitenAnalysisReport
from app.models.keystats import RawKeyStats

router = APIRouter(prefix="/emiten", tags=["Emiten Analysis"])
emiten_service = EmitenService()


@router.get("/list", response_model=List[str])
def list_tickers():
    """List all available tickers in the database/cache."""
    return emiten_service.list_all_available_tickers()


@router.get("/search", response_model=List[RawKeyStats])
def search_emitens(q: str = Query(..., min_length=1, description="Search query for ticker or company name")):
    """Search emitens by ticker or name."""
    return emiten_service.search_emitens(q)


@router.get("/{ticker}", response_model=EmitenAnalysisReport)
def get_single_emiten_analysis(
    ticker: str,
    price: Optional[float] = Query(None, description="Simulate with custom/override market price (IDR)"),
    live: bool = Query(True, description="Fetch live realtime quote from IDX/Yahoo Finance")
):
    """Calculates full KeyStats, Multi-Model Valuation, and 5-Pillar Score for a single emiten with realtime or simulated price."""
    report = emiten_service.analyze_single_emiten(ticker, override_price=price, force_live=live)
    if not report:
        raise HTTPException(status_code=404, detail=f"Emiten with ticker '{ticker.upper()}' not found or data unavailable.")
    return report
