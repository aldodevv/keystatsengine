"""
Domain models for Screener Filters, Presets, and Comparison.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ScreenerPreset(str, Enum):
    CUSTOM = "CUSTOM"
    BUFFETT_MOAT = "BUFFETT_MOAT"          # High ROIC, Low Debt, High Piotroski
    DIVIDEND_CASH_COW = "DIVIDEND_CASH_COW"  # High Yield, Safe DPR, Positive FCF
    GARP = "GARP"                          # Growth at Reasonable Price (Low PEG, High Growth)
    DEEP_VALUE = "DEEP_VALUE"              # Low PBV/PER, Safe Altman Z
    MOMENTUM_QUALITY = "MOMENTUM_QUALITY"  # High Margin Expansion + Strong EPS Growth


class ScreenerCriteria(BaseModel):
    preset: Optional[ScreenerPreset] = None
    sectors: Optional[List[str]] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    
    # Valuation Filters
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_pbv: Optional[float] = None
    max_pbv: Optional[float] = None
    max_peg: Optional[float] = None
    min_upside_pct: Optional[float] = None
    
    # Profitability Filters
    min_roe: Optional[float] = None
    min_npm: Optional[float] = None
    min_roic: Optional[float] = None
    
    # Health & Quality
    max_der: Optional[float] = None
    min_altman_z: Optional[float] = None
    min_piotroski_f: Optional[int] = None
    min_current_ratio: Optional[float] = None
    
    # Dividend & Cash Flow
    min_dividend_yield: Optional[float] = None
    max_dpr: Optional[float] = None
    must_have_positive_fcf: bool = False
    
    # Growth
    min_revenue_growth: Optional[float] = None
    min_eps_growth: Optional[float] = None
    
    # Score
    min_composite_score: Optional[float] = None


class EmitenSummaryItem(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    market_cap: float
    per: float
    pbv: float
    roe: float
    der: float
    piotroski_f_score: int
    altman_z_score: float
    dividend_yield: float
    composite_score: float
    grade: str
    verdict: str
    upside_pct: float


class ScreenerResponse(BaseModel):
    total_matched: int
    results: List[EmitenSummaryItem]
    applied_preset: Optional[str] = None


class ComparisonResponse(BaseModel):
    tickers: List[str]
    items: List[EmitenSummaryItem]
    detailed_reports: List[dict]
    best_in_class: dict  # metric_name -> ticker
