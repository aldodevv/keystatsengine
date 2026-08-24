"""
Domain models for Calculated KeyStats, Composite Scores, Valuation Models, and AI Verdicts.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class HealthZone(str, Enum):
    SAFE = "SAFE"
    GREY = "GREY"
    DISTRESS = "DISTRESS"


class VerdictAction(str, Enum):
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SPECULATIVE = "SPECULATIVE"
    AVOID = "AVOID"


class ValuationResult(BaseModel):
    per: float = 0.0
    pbv: float = 0.0
    ev_ebitda: float = 0.0
    peg_ratio: Optional[float] = None
    graham_number: Optional[float] = None
    dcf_fair_value: Optional[float] = None
    historical_pe_band_status: Optional[str] = None  # e.g. "-1 Std Dev (Undervalued)"
    historical_pbv_band_status: Optional[str] = None
    average_fair_value: float = 0.0
    upside_downside_pct: float = 0.0
    is_undervalued: bool = False


class ProfitabilityResult(BaseModel):
    roe: float = 0.0  # %
    roa: float = 0.0  # %
    roic: float = 0.0  # %
    roce: float = 0.0  # %
    gpm: float = 0.0  # %
    opm: float = 0.0  # %
    npm: float = 0.0  # %
    # DuPont 3-Way Breakdown
    dupont_net_margin: float = 0.0
    dupont_asset_turnover: float = 0.0
    dupont_equity_multiplier: float = 0.0


class SolvencyResult(BaseModel):
    der: float = 0.0
    net_debt_to_equity: float = 0.0
    interest_coverage_ratio: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    altman_z_score: float = 0.0
    altman_zone: HealthZone = HealthZone.SAFE


class QualityScoreResult(BaseModel):
    piotroski_f_score: int = Field(..., ge=0, le=9)
    piotroski_details: Dict[str, bool] = Field(default_factory=dict)
    beneish_m_score: Optional[float] = None
    is_manipulation_risk: bool = False
    cfo_to_net_income: float = 0.0  # Quality of earnings: CFO > Net Income


class LiquidityResult(BaseModel):
    current_ratio: float = 0.0
    quick_ratio: float = 0.0
    cash_ratio: float = 0.0
    working_capital: float = 0.0


class CashFlowDividendResult(BaseModel):
    fcf: float = 0.0
    fcf_yield: float = 0.0  # %
    dividend_yield: float = 0.0  # %
    dpr: float = 0.0  # Dividend Payout Ratio %
    cash_dividend_coverage: Optional[float] = None  # FCF / Dividends Paid
    is_dividend_sustainable: bool = False


class GrowthResult(BaseModel):
    revenue_growth_yoy: float = 0.0  # %
    net_income_growth_yoy: float = 0.0  # %
    eps_growth_yoy: float = 0.0  # %
    revenue_cagr_3y: Optional[float] = None
    net_income_cagr_3y: Optional[float] = None


class RadarScore(BaseModel):
    valuation: float = Field(..., ge=0, le=100, description="Score 0-100")
    profitability: float = Field(..., ge=0, le=100, description="Score 0-100")
    financial_health: float = Field(..., ge=0, le=100, description="Score 0-100")
    growth: float = Field(..., ge=0, le=100, description="Score 0-100")
    cash_flow_quality: float = Field(..., ge=0, le=100, description="Score 0-100")


class PriceSensitivityScenario(BaseModel):
    price_change_pct: float
    simulated_price: float
    per: float
    pbv: float
    dividend_yield: float
    upside_pct: float
    composite_score: float
    verdict: str


class EmitenAnalysisReport(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    current_price: float
    previous_close: Optional[float] = None
    price_change_pct: Optional[float] = 0.0
    is_realtime_price: bool = True
    market_cap: float
    
    # Calculated Pillars
    valuation: ValuationResult
    profitability: ProfitabilityResult
    solvency: SolvencyResult
    quality: QualityScoreResult
    liquidity: LiquidityResult
    cash_flow_dividend: CashFlowDividendResult
    growth: GrowthResult
    bank_metrics: Optional[Dict[str, Any]] = None
    
    # Overall Synthetic Scores
    composite_score: float = Field(..., ge=0, le=100, description="Composite Fundamental Score 0-100")
    grade: str = Field(..., description="A+, A, B, C, D, or F")
    radar: RadarScore
    verdict: VerdictAction
    
    # Price Sensitivity Simulation Matrix (for Daily Traders)
    price_sensitivity_scenarios: List[PriceSensitivityScenario] = Field(default_factory=list)
    
    # Insights & Bullet points
    bull_cases: List[str] = Field(default_factory=list)
    bear_cases: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    green_flags: List[str] = Field(default_factory=list)
