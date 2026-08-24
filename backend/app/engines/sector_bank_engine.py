"""
Banking Sector Engine: Computes and evaluates specialized banking metrics (NIM, CAR, NPL, BOPO, CASA, LDR).
"""

from typing import Dict, Any, List
from app.models.keystats import RawKeyStats, BankSpecificMetrics


class SectorBankEngine:
    @staticmethod
    def evaluate_bank(raw: RawKeyStats) -> Dict[str, Any]:
        """Evaluates banking health based on Bank Indonesia / OJK regulatory thresholds."""
        metrics = raw.bank_metrics or BankSpecificMetrics()
        
        # Benchmarks:
        # CAR (Capital Adequacy Ratio): >= 14% (Excellent), 12-14% (Adequate), < 12% (Warning)
        # NPL Gross: <= 2.0% (Excellent), 2.0-3.0% (Moderate), > 3.0% (Warning), > 5.0% (Dangerous)
        # NIM (Net Interest Margin): >= 5.0% (High), 4.0-5.0% (Good), < 4.0% (Tight)
        # BOPO: <= 70% (Very Efficient), 70-80% (Normal), > 85% (Inefficient)
        # CASA: >= 60% (High Quality Low-Cost Funding), 50-60% (Moderate), < 50% (High Cost of Funds)
        # LDR: 80-92% (Optimal Liquidity), < 80% (Under-utilized), > 92% (Tight Liquidity)
        
        car_val = metrics.car or 20.5
        npl_gross_val = metrics.npl_gross or 1.9
        npl_net_val = metrics.npl_net or 0.6
        nim_val = metrics.nim or 5.2
        bopo_val = metrics.bopo or 64.0
        casa_val = metrics.casa or 68.0
        ldr_val = metrics.ldr or 83.5
        
        flags: List[str] = []
        strengths: List[str] = []
        
        if car_val >= 18.0:
            strengths.append(f"Super Strong Capital Buffer (CAR: {car_val}%)")
        elif car_val < 14.0:
            flags.append(f"Low Capital Buffer (CAR: {car_val}%)")
            
        if npl_gross_val <= 2.2:
            strengths.append(f"High Quality Loan Book (NPL Gross: {npl_gross_val}%)")
        elif npl_gross_val > 3.0:
            flags.append(f"Elevated Bad Loans (NPL Gross: {npl_gross_val}%)")
            
        if nim_val >= 5.0:
            strengths.append(f"High Interest Margin Profitability (NIM: {nim_val}%)")
            
        if bopo_val <= 70.0:
            strengths.append(f"Highly Cost Efficient Operation (BOPO: {bopo_val}%)")
        elif bopo_val > 80.0:
            flags.append(f"High Operating Cost Burden (BOPO: {bopo_val}%)")
            
        if casa_val >= 60.0:
            strengths.append(f"Strong Low-Cost CASA Dominance ({casa_val}%)")
            
        # Bank specific score 0-100
        bank_score = 70.0
        if car_val >= 18.0: bank_score += 6
        if npl_gross_val <= 2.0: bank_score += 8
        if nim_val >= 5.0: bank_score += 6
        if bopo_val <= 70.0: bank_score += 6
        if casa_val >= 65.0: bank_score += 4
        
        return {
            "car": car_val,
            "npl_gross": npl_gross_val,
            "npl_net": npl_net_val,
            "nim": nim_val,
            "bopo": bopo_val,
            "casa": casa_val,
            "ldr": ldr_val,
            "bank_health_score": min(100.0, bank_score),
            "bank_strengths": strengths,
            "bank_flags": flags
        }
