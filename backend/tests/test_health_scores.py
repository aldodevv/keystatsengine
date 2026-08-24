"""
Unit tests for Financial Health (Piotroski F, Altman Z, DuPont ROE).
"""

import pytest
from app.engines.financial_health import FinancialHealthEngine
from app.engines.profitability_engine import ProfitabilityEngine
from app.models.keystats import RawKeyStats, FinancialPeriod
from app.models.score import HealthZone


def test_piotroski_f_score_perfect_nine():
    # Setup periods where all 9 criteria improve
    prev = FinancialPeriod(
        year=2023,
        revenue=100.0,
        gross_profit=40.0,
        operating_profit=20.0,
        net_income=10.0,
        total_assets=100.0,
        current_assets=50.0,
        current_liabilities=30.0,
        long_term_debt=20.0,
        cfo=12.0,
        shares_outstanding=10.0
    )
    curr = FinancialPeriod(
        year=2024,
        revenue=120.0,          # rev up
        gross_profit=54.0,      # GPM 45% vs 40% (improves)
        operating_profit=25.0,
        net_income=15.0,        # ROA 12.5% vs 10% (improves)
        total_assets=120.0,     # Asset turn 1.0 vs 1.0 (same/better)
        current_assets=70.0,    # Current ratio 70/35 = 2.0 vs 50/30 = 1.67 (improves)
        current_liabilities=35.0,
        long_term_debt=18.0,    # Debt ratio 18/120 = 0.15 vs 20/100 = 0.20 (improves)
        cfo=20.0,               # CFO > Net Income (improves)
        shares_outstanding=10.0 # No dilution
    )
    raw = RawKeyStats(
        ticker="PERF",
        name="Perfect Stock Tbk",
        current_price=100.0,
        shares_outstanding=10.0,
        market_cap=1000.0,
        current_period=curr,
        previous_period=prev
    )
    
    qual = FinancialHealthEngine.calculate_quality(raw)
    assert qual.piotroski_f_score == 9
    assert qual.cfo_to_net_income == pytest.approx(1.33, rel=1e-2)


def test_dupont_roe_identity():
    # ROE = Net Margin * Asset Turnover * Equity Multiplier
    # (15/100) * (100/200) * (200/50) = 0.15 * 0.5 * 4 = 0.30 (30%)
    raw = RawKeyStats(
        ticker="DUPONT",
        name="DuPont Test Tbk",
        current_price=100.0,
        shares_outstanding=1.0,
        market_cap=100.0,
        current_period=FinancialPeriod(
            year=2024,
            revenue=100.0,
            gross_profit=40.0,
            operating_profit=20.0,
            net_income=15.0,
            total_assets=200.0,
            total_equity=50.0,
            current_liabilities=50.0
        )
    )
    prof = ProfitabilityEngine.calculate(raw)
    assert prof.roe == 30.0
    assert prof.dupont_net_margin == 0.15
    assert prof.dupont_asset_turnover == 0.5
    assert prof.dupont_equity_multiplier == 4.0
    # Identity test: Net Margin * Asset Turn * Eq Mult * 100 == ROE
    calculated_roe = prof.dupont_net_margin * prof.dupont_asset_turnover * prof.dupont_equity_multiplier * 100
    assert pytest.approx(calculated_roe, rel=1e-3) == prof.roe
