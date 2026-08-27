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


def test_growth_and_cagr_calculation():
    p2021 = FinancialPeriod(year=2021, revenue=100.0, net_income=10.0, eps=10.0)
    p2022 = FinancialPeriod(year=2022, revenue=110.0, net_income=12.0, eps=12.0)
    p2023 = FinancialPeriod(year=2023, revenue=125.0, net_income=15.0, eps=15.0)
    p2024 = FinancialPeriod(year=2024, revenue=150.0, net_income=20.0, eps=20.0)
    
    raw = RawKeyStats(
        ticker="GROWTH",
        name="Growth Co Tbk",
        current_price=200.0,
        shares_outstanding=1.0,
        market_cap=200.0,
        current_period=p2024,
        previous_period=p2023,
        historical_periods=[p2023, p2022, p2021]
    )
    
    growth = FinancialHealthEngine.calculate_growth(raw)
    assert growth.revenue_growth_yoy == pytest.approx(20.0, rel=1e-2)  # (150-125)/125 = 20%
    assert growth.net_income_growth_yoy == pytest.approx(33.33, rel=1e-2)  # (20-15)/15 = 33.33%
    assert growth.eps_growth_yoy == pytest.approx(33.33, rel=1e-2)
    assert growth.eps_current == 20.0
    assert growth.revenue_current == 150.0
    
    # 3Y CAGR: (150/100)^(1/3) - 1 = 14.47%
    assert growth.revenue_cagr_3y == pytest.approx(14.47, rel=1e-2)
    # EPS CAGR: (20/10)^(1/3) - 1 = 25.99%
    assert growth.eps_cagr_3y == pytest.approx(25.99, rel=1e-2)
    assert len(growth.revenue_history) == 4
    assert len(growth.eps_history) == 4


def test_mock_provider_all_emitens_have_complete_data():
    from app.data_providers.mock_provider import MockDataProvider
    from app.engines.scoring_engine import ScoringEngine
    
    provider = MockDataProvider()
    tickers = provider.list_all_tickers()
    assert len(tickers) >= 10
    assert "ADMR" in tickers
    
    for t in tickers:
        raw = provider.get_keystats(t)
        assert raw is not None
        assert raw.current_period.eps > 0
        assert raw.current_period.revenue > 0
        assert raw.current_period.net_income > 0
        assert raw.previous_period is not None
        assert len(raw.historical_periods) >= 3
        assert raw.financial_matrix is not None
        
        report = ScoringEngine.analyze_emiten(raw)
        assert report.eps > 0
        assert report.revenue > 0
        assert report.net_income > 0
        assert report.financial_matrix is not None
        assert len(report.financial_matrix.years) >= 5


def test_admr_stockbit_matrix():
    from app.data_providers.mock_provider import MockDataProvider
    from app.engines.scoring_engine import ScoringEngine

    provider = MockDataProvider()
    admr = provider.get_keystats("ADMR")
    assert admr is not None
    assert admr.ticker == "ADMR"
    assert admr.current_price == 1715.0
    assert admr.current_period.revenue == 17_269_000_000_000.0  # Rp 17.27 T
    assert admr.current_period.net_income == 4_871_000_000_000.0  # Rp 4.87 T
    assert admr.current_period.eps == 119.14

    report = ScoringEngine.analyze_emiten(admr)
    assert report.financial_matrix is not None
    mat = report.financial_matrix
    assert 2026 in mat.years
    assert mat.eps_matrix["2026"].q1 == 35.17
    assert mat.eps_matrix["2026"].annualised == 144.67
    assert mat.eps_matrix["2026"].ttm == 119.14
    assert mat.revenue_matrix["2026"].ttm == 17_269_000_000_000.0
    assert mat.income_statement_ttm.revenue_ttm == 17_269_000_000_000.0
    assert mat.balance_sheet_quarter.cash == 8_571_000_000_000.0

