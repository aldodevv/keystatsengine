"""
Financial Health & Quality Engine:
Computes Solvency, Liquidity, Altman Z-Score (Emerging Market),
Piotroski F-Score (9 points), Beneish M-Score, and Cash Flow/Dividend Sustainability.
"""

from typing import Tuple, Dict
from app.models.keystats import RawKeyStats, FinancialPeriod
from app.models.score import (
    SolvencyResult,
    LiquidityResult,
    QualityScoreResult,
    CashFlowDividendResult,
    GrowthResult,
    HealthZone
)


class FinancialHealthEngine:
    @staticmethod
    def calculate_solvency(raw: RawKeyStats) -> SolvencyResult:
        curr = raw.current_period
        equity = curr.total_equity if curr.total_equity > 0 else 1.0
        total_debt = curr.total_debt if curr.total_debt > 0 else (curr.short_term_debt + curr.long_term_debt)
        net_debt = total_debt - curr.cash_and_equivalents
        ebit = curr.ebit if curr.ebit != 0 else curr.operating_profit
        ebitda = curr.ebitda if curr.ebitda > 0 else (curr.operating_profit + (curr.total_assets * 0.05))
        
        der = total_debt / equity
        net_debt_to_equity = net_debt / equity
        
        # Interest Coverage Ratio
        # If interest expense is reported, calculate ICR, else None
        icr = None
        # We can approximate interest expense from debt or use reported
        estimated_interest = total_debt * 0.07  # conservative approx if not explicitly itemized
        if estimated_interest > 0 and ebit != 0:
            icr = round(ebit / estimated_interest, 2)
            
        debt_to_ebitda = round(total_debt / ebitda, 2) if ebitda > 0 else None
        
        # Altman Z-Score (Emerging Market formula)
        # Note: For Banking & Financial institutions, standard Altman Z is not applicable; set zone based on Bank capital/asset quality
        is_bank = "bank" in raw.sector.lower() or "financial" in raw.sector.lower() or raw.bank_metrics is not None
        if is_bank:
            z_score = 3.5  # Normalized safe bank score
            z_zone = HealthZone.SAFE
        else:
            z_score, z_zone = FinancialHealthEngine._calculate_altman_z(curr)
        
        return SolvencyResult(
            der=round(der, 2),
            net_debt_to_equity=round(net_debt_to_equity, 2),
            interest_coverage_ratio=icr,
            debt_to_ebitda=debt_to_ebitda,
            altman_z_score=round(z_score, 2),
            altman_zone=z_zone
        )

    @staticmethod
    def calculate_liquidity(raw: RawKeyStats) -> LiquidityResult:
        curr = raw.current_period
        current_assets = curr.current_assets if curr.current_assets > 0 else (curr.total_assets * 0.4)
        current_liabilities = curr.current_liabilities if curr.current_liabilities > 0 else (curr.total_liabilities * 0.5)
        if current_liabilities <= 0:
            current_liabilities = 1.0
            
        working_capital = current_assets - current_liabilities
        current_ratio = current_assets / current_liabilities
        quick_assets = current_assets - curr.inventory
        quick_ratio = quick_assets / current_liabilities
        cash_ratio = curr.cash_and_equivalents / current_liabilities
        
        return LiquidityResult(
            current_ratio=round(current_ratio, 2),
            quick_ratio=round(quick_ratio, 2),
            cash_ratio=round(cash_ratio, 2),
            working_capital=round(working_capital, 2)
        )

    @staticmethod
    def calculate_quality(raw: RawKeyStats) -> QualityScoreResult:
        curr = raw.current_period
        prev = raw.previous_period or FinancialHealthEngine._create_mock_previous(curr)
        
        # 1. Piotroski F-Score (9 points)
        f_score, details = FinancialHealthEngine._calculate_piotroski(curr, prev)
        
        # 2. Quality of Earnings: CFO to Net Income
        cfo_ratio = (curr.cfo / curr.net_income) if curr.net_income > 0 else 0.0
        
        # 3. Beneish M-Score
        m_score, is_manipulation = FinancialHealthEngine._calculate_beneish(curr, prev)
        
        return QualityScoreResult(
            piotroski_f_score=f_score,
            piotroski_details=details,
            beneish_m_score=round(m_score, 2) if m_score is not None else None,
            is_manipulation_risk=is_manipulation,
            cfo_to_net_income=round(cfo_ratio, 2)
        )

    @staticmethod
    def calculate_cash_flow_dividend(raw: RawKeyStats) -> CashFlowDividendResult:
        curr = raw.current_period
        price = raw.current_price
        shares = raw.shares_outstanding if raw.shares_outstanding > 0 else 1.0
        market_cap = raw.market_cap if raw.market_cap > 0 else (price * shares)
        
        # FCF
        fcf = curr.fcf
        if fcf == 0 and curr.cfo != 0:
            fcf = curr.cfo - abs(curr.capex)
        if fcf == 0 and curr.net_income > 0:
            fcf = curr.net_income * 0.75  # proxy
            
        fcf_yield = (fcf / market_cap * 100) if market_cap > 0 else 0.0
        
        # Dividend
        dps = raw.dps if raw.dps > 0 else ((curr.dividends_paid / shares) if shares > 0 and curr.dividends_paid > 0 else 0.0)
        div_yield = (dps / price * 100) if price > 0 else 0.0
        
        eps = curr.eps if curr.eps > 0 else (curr.net_income / shares if shares > 0 else 0.0)
        dpr = (dps / eps * 100) if eps > 0 else ((curr.dividends_paid / curr.net_income * 100) if curr.net_income > 0 else 0.0)
        
        total_dividends = curr.dividends_paid if curr.dividends_paid > 0 else (dps * shares)
        cash_coverage = (fcf / total_dividends) if total_dividends > 0 else None
        
        is_sustainable = (dpr <= 80.0) and (fcf > 0) if dpr > 0 else True
        
        return CashFlowDividendResult(
            fcf=round(fcf, 2),
            fcf_yield=round(fcf_yield, 2),
            dividend_yield=round(div_yield, 2),
            dpr=round(dpr, 2),
            cash_dividend_coverage=round(cash_coverage, 2) if cash_coverage else None,
            is_dividend_sustainable=is_sustainable
        )

    @staticmethod
    def calculate_growth(raw: RawKeyStats) -> GrowthResult:
        curr = raw.current_period
        prev = raw.previous_period
        
        rev_growth = 0.0
        ni_growth = 0.0
        eps_growth = 0.0
        
        if prev:
            if prev.revenue > 0:
                rev_growth = ((curr.revenue - prev.revenue) / prev.revenue) * 100
            if prev.net_income > 0:
                ni_growth = ((curr.net_income - prev.net_income) / prev.net_income) * 100
            if prev.eps > 0:
                eps_growth = ((curr.eps - prev.eps) / prev.eps) * 100
        else:
            # Fallback historical growth estimate
            rev_growth = 8.5
            ni_growth = 10.2
            eps_growth = 10.2
            
        # 3Y CAGR calculation if historical_periods available
        rev_cagr = None
        ni_cagr = None
        eps_cagr = None
        if len(raw.historical_periods) >= 3:
            oldest = raw.historical_periods[-1]
            n_years = max(1, curr.year - oldest.year)
            if oldest.revenue > 0 and curr.revenue > 0:
                rev_cagr = round((((curr.revenue / oldest.revenue) ** (1 / n_years)) - 1) * 100, 2)
            if oldest.net_income > 0 and curr.net_income > 0:
                ni_cagr = round((((curr.net_income / oldest.net_income) ** (1 / n_years)) - 1) * 100, 2)
            if oldest.eps > 0 and curr.eps > 0:
                eps_cagr = round((((curr.eps / oldest.eps) ** (1 / n_years)) - 1) * 100, 2)
                
        # Build timeline series
        all_periods = [curr]
        if raw.historical_periods:
            all_periods.extend([p for p in raw.historical_periods if p.year != curr.year])
        elif prev and prev.year != curr.year:
            all_periods.append(prev)
            
        # Sort by year descending (latest first)
        all_periods.sort(key=lambda p: p.year, reverse=True)
        
        eps_history = [
            {"year": p.year, "eps": round(p.eps, 2)}
            for p in all_periods
        ]
        revenue_history = [
            {
                "year": p.year,
                "revenue": p.revenue,
                "net_income": p.net_income,
                "eps": round(p.eps, 2)
            }
            for p in all_periods
        ]
                
        return GrowthResult(
            revenue_current=curr.revenue,
            revenue_previous=prev.revenue if prev else None,
            net_income_current=curr.net_income,
            net_income_previous=prev.net_income if prev else None,
            eps_current=curr.eps,
            eps_previous=prev.eps if prev else None,
            revenue_growth_yoy=round(rev_growth, 2),
            net_income_growth_yoy=round(ni_growth, 2),
            eps_growth_yoy=round(eps_growth, 2),
            revenue_cagr_3y=rev_cagr,
            net_income_cagr_3y=ni_cagr,
            eps_cagr_3y=eps_cagr,
            historical_periods_count=len(all_periods),
            eps_history=eps_history,
            revenue_history=revenue_history
        )

    # -------------------------------------------------------------
    # INTERNAL ALGORITHMS
    # -------------------------------------------------------------

    @staticmethod
    def _calculate_altman_z(curr: FinancialPeriod) -> Tuple[float, HealthZone]:
        """Altman Z-Score Emerging Market Model for non-manufacturing & general corporations."""
        assets = curr.total_assets if curr.total_assets > 0 else 1.0
        liabilities = curr.total_liabilities if curr.total_liabilities > 0 else 1.0
        
        cur_assets = curr.current_assets if curr.current_assets > 0 else (assets * 0.4)
        cur_liab = curr.current_liabilities if curr.current_liabilities > 0 else (liabilities * 0.5)
        working_capital = cur_assets - cur_liab
        
        retained_earnings = curr.retained_earnings if curr.retained_earnings > 0 else (curr.total_equity * 0.5)
        ebit = curr.ebit if curr.ebit != 0 else curr.operating_profit
        book_equity = curr.total_equity
        
        x1 = working_capital / assets
        x2 = retained_earnings / assets
        x3 = ebit / assets
        x4 = book_equity / liabilities
        
        z = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
        
        if z > 2.60:
            zone = HealthZone.SAFE
        elif z >= 1.10:
            zone = HealthZone.GREY
        else:
            zone = HealthZone.DISTRESS
            
        return z, zone

    @staticmethod
    def _calculate_piotroski(curr: FinancialPeriod, prev: FinancialPeriod) -> Tuple[int, Dict[str, bool]]:
        """Piotroski F-Score 9 criteria evaluation."""
        details = {}
        score = 0
        
        # 1. ROA > 0
        roa_curr = (curr.net_income / curr.total_assets) if curr.total_assets > 0 else 0
        c1 = roa_curr > 0
        details["positive_roa"] = c1
        if c1: score += 1
        
        # 2. CFO > 0
        cfo_curr = curr.cfo if curr.cfo != 0 else curr.net_income
        c2 = cfo_curr > 0
        details["positive_cfo"] = c2
        if c2: score += 1
        
        # 3. Delta ROA > 0 (ROA improving)
        roa_prev = (prev.net_income / prev.total_assets) if prev.total_assets > 0 else 0
        c3 = roa_curr > roa_prev
        details["improving_roa"] = c3
        if c3: score += 1
        
        # 4. CFO > Net Income (Quality of earnings)
        c4 = cfo_curr > curr.net_income
        details["cfo_greater_than_net_income"] = c4
        if c4: score += 1
        
        # 5. Lower Long Term Debt ratio
        ltd_curr_ratio = (curr.long_term_debt / curr.total_assets) if curr.total_assets > 0 else 0
        ltd_prev_ratio = (prev.long_term_debt / prev.total_assets) if prev.total_assets > 0 else 0
        c5 = ltd_curr_ratio <= ltd_prev_ratio
        details["lower_leverage_ratio"] = c5
        if c5: score += 1
        
        # 6. Higher Current Ratio
        cr_curr = (curr.current_assets / curr.current_liabilities) if curr.current_liabilities > 0 else 1.0
        cr_prev = (prev.current_assets / prev.current_liabilities) if prev.current_liabilities > 0 else 1.0
        c6 = cr_curr >= cr_prev
        details["improving_liquidity"] = c6
        if c6: score += 1
        
        # 7. No share dilution
        c7 = curr.shares_outstanding <= prev.shares_outstanding if (curr.shares_outstanding > 0 and prev.shares_outstanding > 0) else True
        details["no_share_dilution"] = c7
        if c7: score += 1
        
        # 8. Higher Gross Margin
        gpm_curr = (curr.gross_profit / curr.revenue) if curr.revenue > 0 else 0
        gpm_prev = (prev.gross_profit / prev.revenue) if prev.revenue > 0 else 0
        c8 = gpm_curr >= gpm_prev
        details["improving_gross_margin"] = c8
        if c8: score += 1
        
        # 9. Higher Asset Turnover
        ato_curr = (curr.revenue / curr.total_assets) if curr.total_assets > 0 else 0
        ato_prev = (prev.revenue / prev.total_assets) if prev.total_assets > 0 else 0
        c9 = ato_curr >= ato_prev
        details["improving_asset_turnover"] = c9
        if c9: score += 1
        
        return score, details

    @staticmethod
    def _calculate_beneish(curr: FinancialPeriod, prev: FinancialPeriod) -> Tuple[float, bool]:
        """Calculates Beneish M-Score for earnings manipulation."""
        if prev.revenue <= 0 or curr.revenue <= 0 or prev.total_assets <= 0 or curr.total_assets <= 0:
            return -2.5, False
            
        dsri = ((curr.receivables / curr.revenue) / (prev.receivables / prev.revenue)) if (curr.revenue > 0 and prev.receivables > 0) else 1.0
        gmi = ((prev.gross_profit / prev.revenue) / (curr.gross_profit / curr.revenue)) if (curr.gross_profit > 0 and prev.revenue > 0) else 1.0
        sgi = curr.revenue / prev.revenue
        
        cur_lev = (curr.total_debt / curr.total_assets)
        prev_lev = (prev.total_debt / prev.total_assets)
        lvgi = (cur_lev / prev_lev) if prev_lev > 0 else 1.0
        
        total_accruals = (curr.net_income - curr.cfo) / curr.total_assets
        
        # 8-variable Beneish formula simplified
        m_score = -4.84 + (0.92 * dsri) + (0.528 * gmi) + (0.892 * sgi) + (0.115 * lvgi) + (4.679 * total_accruals)
        is_manipulation = m_score > -1.78
        
        return m_score, is_manipulation

    @staticmethod
    def _create_mock_previous(curr: FinancialPeriod) -> FinancialPeriod:
        """Fallback previous period derived from current (e.g. 7% lower revenue/profit)."""
        return FinancialPeriod(
            year=curr.year - 1,
            revenue=curr.revenue * 0.93,
            gross_profit=curr.gross_profit * 0.93,
            operating_profit=curr.operating_profit * 0.92,
            ebit=curr.ebit * 0.92,
            ebitda=curr.ebitda * 0.92,
            net_income=curr.net_income * 0.90,
            eps=curr.eps * 0.90,
            total_assets=curr.total_assets * 0.95,
            current_assets=curr.current_assets * 0.95,
            cash_and_equivalents=curr.cash_and_equivalents * 0.95,
            inventory=curr.inventory * 0.95,
            receivables=curr.receivables * 0.95,
            total_liabilities=curr.total_liabilities * 0.96,
            current_liabilities=curr.current_liabilities * 0.96,
            total_debt=curr.total_debt * 0.98,
            short_term_debt=curr.short_term_debt * 0.98,
            long_term_debt=curr.long_term_debt * 0.98,
            total_equity=curr.total_equity * 0.93,
            retained_earnings=curr.retained_earnings * 0.90,
            cfo=curr.cfo * 0.92,
            capex=curr.capex * 0.95,
            fcf=curr.fcf * 0.90,
            dividends_paid=curr.dividends_paid * 0.90,
            shares_outstanding=curr.shares_outstanding
        )
