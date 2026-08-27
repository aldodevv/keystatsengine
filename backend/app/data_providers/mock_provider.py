"""
Mock & Seed Data Provider: Contains realistic IDX financial statements,
KeyStats, multi-year historical periods (2021-2024), and sector metrics for high-speed offline analysis and testing.
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
import math
from app.data_providers.base import BaseDataProvider
from app.models.keystats import RawKeyStats, FinancialPeriod, BankSpecificMetrics
from app.models.chart import CandleDataPoint


class MockDataProvider(BaseDataProvider):
    def __init__(self):
        self._dataset: Dict[str, RawKeyStats] = self._init_dataset()

    def get_keystats(
        self,
        ticker: str,
        override_price: Optional[float] = None,
        force_live: bool = False
    ) -> Optional[RawKeyStats]:
        clean_ticker = ticker.upper().replace(".JK", "").strip()
        data = self._dataset.get(clean_ticker)
        if data and override_price is not None and override_price > 0:
            import copy
            data = copy.deepcopy(data)
            data.current_price = override_price
        return data

    def list_all_tickers(self) -> List[str]:
        return list(self._dataset.keys())

    def search_tickers(self, query: str) -> List[RawKeyStats]:
        q = query.upper().strip()
        return [
            v for k, v in self._dataset.items()
            if q in k or q in v.name.upper() or q in v.sector.upper()
        ]

    def get_historical_ohlcv(self, ticker: str, timeframe: str = "1y") -> List[CandleDataPoint]:
        clean_ticker = ticker.upper().replace(".JK", "").strip()
        ks = self._dataset.get(clean_ticker)
        current_price = ks.current_price if ks else 3000.0
        
        days_map = {
            "1mo": 25,
            "3mo": 65,
            "6mo": 130,
            "1y": 250,
            "5y": 500
        }
        num_days = days_map.get(timeframe.lower(), 250)
        
        # Deterministic generation backwards from current date & current_price
        end_date = datetime.now()
        seed_offset = sum(ord(c) for c in clean_ticker)
        
        candles: List[CandleDataPoint] = []
        
        # Build price path with realistic sine waves, volatility, and trend
        prices: List[float] = [current_price]
        curr = current_price
        
        for i in range(1, num_days):
            # Deterministic wave + noise
            wave = math.sin((i + seed_offset) * 0.15) * 0.012
            noise = math.cos((i * 7 + seed_offset) * 0.25) * 0.015
            drift = -0.0003  # slight upward drift forward (so backward is downward)
            
            # Occasional gap simulation
            gap = 0.0
            if (i + seed_offset) % 37 == 0:
                gap = 0.025 * (1 if math.sin(i) > 0 else -1)
                
            pct_change = wave + noise + drift + gap
            curr = curr * (1.0 - pct_change)  # going backward
            prices.append(max(curr, 50.0))
            
        prices.reverse()  # now prices are chronological
        
        # Generate OHLCV candles
        base_vol = int(ks.market_cap / 1e8) if ks else 5000000
        for i, p_close in enumerate(prices):
            # Calculate date (skipping weekends)
            day_delta = num_days - 1 - i
            # rough trading day mapping
            d = end_date - timedelta(days=int(day_delta * 1.45))
            date_str = d.strftime("%Y-%m-%d")
            
            intra_vol = 0.015
            p_open = p_close * (1.0 + math.sin(i * 3 + seed_offset) * intra_vol * 0.5)
            p_high = max(p_open, p_close) * (1.0 + abs(math.cos(i * 5 + seed_offset)) * intra_vol)
            p_low = min(p_open, p_close) * (1.0 - abs(math.sin(i * 4 + seed_offset)) * intra_vol)
            
            # Volume with breakout spike
            vol_multiplier = 1.0 + abs(math.sin(i * 2 + seed_offset)) * 0.8
            if (i + seed_offset) % 45 == 0:
                vol_multiplier *= 2.8  # Volume breakout spike
            
            vol = int(base_vol * vol_multiplier)
            
            candles.append(CandleDataPoint(
                time=date_str,
                open=round(p_open, 2),
                high=round(p_high, 2),
                low=round(p_low, 2),
                close=round(p_close, 2),
                volume=vol
            ))
            
        return candles

    def _init_dataset(self) -> Dict[str, RawKeyStats]:
        data: Dict[str, RawKeyStats] = {}

        # -------------------------------------------------------------
        # 1. BBRI (Bank Rakyat Indonesia) - Banking Giant
        # -------------------------------------------------------------
        p2024_bbri = FinancialPeriod(
            year=2024,
            revenue=198_500_000_000_000,
            gross_profit=165_000_000_000_000,
            operating_profit=74_200_000_000_000,
            ebit=74_200_000_000_000,
            ebitda=79_500_000_000_000,
            net_income=60_425_000_000_000,
            eps=398.69,
            total_assets=1_965_000_000_000_000,
            current_assets=580_000_000_000_000,
            cash_and_equivalents=190_000_000_000_000,
            inventory=0.0,
            receivables=45_000_000_000_000,
            total_liabilities=1_648_000_000_000_000,
            current_liabilities=1_420_000_000_000_000,
            total_debt=220_000_000_000_000,
            short_term_debt=80_000_000_000_000,
            long_term_debt=140_000_000_000_000,
            total_equity=317_000_000_000_000,
            retained_earnings=210_000_000_000_000,
            cfo=65_000_000_000_000,
            capex=12_000_000_000_000,
            fcf=53_000_000_000_000,
            dividends_paid=48_347_000_000_000,
            shares_outstanding=151_559_000_000
        )
        p2023_bbri = FinancialPeriod(
            year=2023,
            revenue=178_000_000_000_000,
            gross_profit=148_000_000_000_000,
            operating_profit=68_500_000_000_000,
            ebit=68_500_000_000_000,
            ebitda=73_000_000_000_000,
            net_income=54_500_000_000_000,
            eps=359.59,
            total_assets=1_865_000_000_000_000,
            current_assets=530_000_000_000_000,
            cash_and_equivalents=175_000_000_000_000,
            inventory=0.0,
            receivables=40_000_000_000_000,
            total_liabilities=1_570_000_000_000_000,
            current_liabilities=1_350_000_000_000_000,
            total_debt=210_000_000_000_000,
            short_term_debt=75_000_000_000_000,
            long_term_debt=135_000_000_000_000,
            total_equity=295_000_000_000_000,
            retained_earnings=190_000_000_000_000,
            cfo=58_000_000_000_000,
            capex=11_000_000_000_000,
            fcf=47_000_000_000_000,
            dividends_paid=43_000_000_000_000,
            shares_outstanding=151_559_000_000
        )
        p2022_bbri = FinancialPeriod(
            year=2022,
            revenue=156_400_000_000_000,
            gross_profit=130_000_000_000_000,
            operating_profit=63_200_000_000_000,
            ebit=63_200_000_000_000,
            ebitda=67_500_000_000_000,
            net_income=51_410_000_000_000,
            eps=339.20,
            total_assets=1_750_000_000_000_000,
            current_assets=490_000_000_000_000,
            cash_and_equivalents=160_000_000_000_000,
            inventory=0.0,
            receivables=36_000_000_000_000,
            total_liabilities=1_480_000_000_000_000,
            current_liabilities=1_270_000_000_000_000,
            total_debt=195_000_000_000_000,
            short_term_debt=70_000_000_000_000,
            long_term_debt=125_000_000_000_000,
            total_equity=270_000_000_000_000,
            retained_earnings=172_000_000_000_000,
            cfo=52_000_000_000_000,
            capex=10_000_000_000_000,
            fcf=42_000_000_000_000,
            dividends_paid=38_500_000_000_000,
            shares_outstanding=151_559_000_000
        )
        p2021_bbri = FinancialPeriod(
            year=2021,
            revenue=143_500_000_000_000,
            gross_profit=118_000_000_000_000,
            operating_profit=39_800_000_000_000,
            ebit=39_800_000_000_000,
            ebitda=44_200_000_000_000,
            net_income=30_760_000_000_000,
            eps=202.96,
            total_assets=1_678_000_000_000_000,
            current_assets=460_000_000_000_000,
            cash_and_equivalents=150_000_000_000_000,
            inventory=0.0,
            receivables=32_000_000_000_000,
            total_liabilities=1_420_000_000_000_000,
            current_liabilities=1_220_000_000_000_000,
            total_debt=180_000_000_000_000,
            short_term_debt=65_000_000_000_000,
            long_term_debt=115_000_000_000_000,
            total_equity=258_000_000_000_000,
            retained_earnings=155_000_000_000_000,
            cfo=45_000_000_000_000,
            capex=9_000_000_000_000,
            fcf=36_000_000_000_000,
            dividends_paid=20_500_000_000_000,
            shares_outstanding=151_559_000_000
        )

        data["BBRI"] = RawKeyStats(
            ticker="BBRI",
            name="Bank Rakyat Indonesia (Persero) Tbk",
            sector="Financials",
            industry="Banking",
            current_price=4750.0,
            shares_outstanding=151_559_000_000,
            market_cap=719_905_250_000_000,
            dps=319.0,
            beta=1.15,
            pe_mean_5y=14.2,
            pe_standard_deviation=2.1,
            pbv_mean_5y=2.45,
            pbv_standard_deviation=0.35,
            is_syariah=False,
            current_period=p2024_bbri,
            previous_period=p2023_bbri,
            historical_periods=[p2023_bbri, p2022_bbri, p2021_bbri],
            bank_metrics=BankSpecificMetrics(
                car=26.8,
                npl_gross=2.95,
                npl_net=0.75,
                nim=6.85,
                bopo=66.8,
                ldr=87.2,
                casa=64.2,
                cost_of_credit=3.4
            )
        )

        # -------------------------------------------------------------
        # 2. BBCA (Bank Central Asia) - Blue Chip Quality Leader
        # -------------------------------------------------------------
        p2024_bbca = FinancialPeriod(
            year=2024,
            revenue=108_500_000_000_000,
            gross_profit=96_000_000_000_000,
            operating_profit=64_000_000_000_000,
            ebit=64_000_000_000_000,
            ebitda=68_500_000_000_000,
            net_income=53_200_000_000_000,
            eps=431.55,
            total_assets=1_440_000_000_000_000,
            current_assets=490_000_000_000_000,
            cash_and_equivalents=210_000_000_000_000,
            inventory=0.0,
            receivables=25_000_000_000_000,
            total_liabilities=1_190_000_000_000_000,
            current_liabilities=1_080_000_000_000_000,
            total_debt=45_000_000_000_000,
            short_term_debt=15_000_000_000_000,
            long_term_debt=30_000_000_000_000,
            total_equity=250_000_000_000_000,
            retained_earnings=205_000_000_000_000,
            cfo=58_000_000_000_000,
            capex=8_500_000_000_000,
            fcf=49_500_000_000_000,
            dividends_paid=33_284_000_000_000,
            shares_outstanding=123_275_000_000
        )
        p2023_bbca = FinancialPeriod(
            year=2023,
            revenue=96_800_000_000_000,
            gross_profit=85_500_000_000_000,
            operating_profit=58_000_000_000_000,
            ebit=58_000_000_000_000,
            ebitda=62_000_000_000_000,
            net_income=48_600_000_000_000,
            eps=394.24,
            total_assets=1_350_000_000_000_000,
            current_assets=450_000_000_000_000,
            cash_and_equivalents=195_000_000_000_000,
            inventory=0.0,
            receivables=22_000_000_000_000,
            total_liabilities=1_125_000_000_000_000,
            current_liabilities=1_020_000_000_000_000,
            total_debt=40_000_000_000_000,
            short_term_debt=12_000_000_000_000,
            long_term_debt=28_000_000_000_000,
            total_equity=225_000_000_000_000,
            retained_earnings=180_000_000_000_000,
            cfo=52_000_000_000_000,
            capex=7_800_000_000_000,
            fcf=44_200_000_000_000,
            dividends_paid=29_500_000_000_000,
            shares_outstanding=123_275_000_000
        )
        p2022_bbca = FinancialPeriod(
            year=2022,
            revenue=87_400_000_000_000,
            gross_profit=76_800_000_000_000,
            operating_profit=49_500_000_000_000,
            ebit=49_500_000_000_000,
            ebitda=53_200_000_000_000,
            net_income=40_740_000_000_000,
            eps=330.48,
            total_assets=1_250_000_000_000_000,
            current_assets=410_000_000_000_000,
            cash_and_equivalents=180_000_000_000_000,
            inventory=0.0,
            receivables=20_000_000_000_000,
            total_liabilities=1_045_000_000_000_000,
            current_liabilities=950_000_000_000_000,
            total_debt=35_000_000_000_000,
            short_term_debt=10_000_000_000_000,
            long_term_debt=25_000_000_000_000,
            total_equity=205_000_000_000_000,
            retained_earnings=162_000_000_000_000,
            cfo=46_000_000_000_000,
            capex=7_000_000_000_000,
            fcf=39_000_000_000_000,
            dividends_paid=25_000_000_000_000,
            shares_outstanding=123_275_000_000
        )
        p2021_bbca = FinancialPeriod(
            year=2021,
            revenue=78_500_000_000_000,
            gross_profit=68_900_000_000_000,
            operating_profit=38_200_000_000_000,
            ebit=38_200_000_000_000,
            ebitda=41_500_000_000_000,
            net_income=31_420_000_000_000,
            eps=254.88,
            total_assets=1_160_000_000_000_000,
            current_assets=380_000_000_000_000,
            cash_and_equivalents=165_000_000_000_000,
            inventory=0.0,
            receivables=18_000_000_000_000,
            total_liabilities=975_000_000_000_000,
            current_liabilities=890_000_000_000_000,
            total_debt=30_000_000_000_000,
            short_term_debt=8_000_000_000_000,
            long_term_debt=22_000_000_000_000,
            total_equity=185_000_000_000_000,
            retained_earnings=145_000_000_000_000,
            cfo=40_000_000_000_000,
            capex=6_200_000_000_000,
            fcf=33_800_000_000_000,
            dividends_paid=17_800_000_000_000,
            shares_outstanding=123_275_000_000
        )

        data["BBCA"] = RawKeyStats(
            ticker="BBCA",
            name="Bank Central Asia Tbk",
            sector="Financials",
            industry="Banking",
            current_price=9850.0,
            shares_outstanding=123_275_000_000,
            market_cap=1_214_258_750_000_000,
            dps=270.0,
            beta=0.82,
            pe_mean_5y=24.5,
            pe_standard_deviation=2.8,
            pbv_mean_5y=4.5,
            pbv_standard_deviation=0.45,
            is_syariah=False,
            current_period=p2024_bbca,
            previous_period=p2023_bbca,
            historical_periods=[p2023_bbca, p2022_bbca, p2021_bbca],
            bank_metrics=BankSpecificMetrics(
                car=29.2,
                npl_gross=1.75,
                npl_net=0.42,
                nim=5.75,
                bopo=48.5,
                ldr=79.5,
                casa=81.6,
                cost_of_credit=0.8
            )
        )

        # -------------------------------------------------------------
        # 3. BMRI (Bank Mandiri) - Corporate & Retail Powerhouse
        # -------------------------------------------------------------
        p2024_bmri = FinancialPeriod(
            year=2024,
            revenue=165_000_000_000_000,
            gross_profit=138_000_000_000_000,
            operating_profit=69_500_000_000_000,
            ebit=69_500_000_000_000,
            ebitda=74_000_000_000_000,
            net_income=55_800_000_000_000,
            eps=597.85,
            total_assets=2_170_000_000_000_000,
            current_assets=620_000_000_000_000,
            cash_and_equivalents=230_000_000_000_000,
            inventory=0.0,
            receivables=38_000_000_000_000,
            total_liabilities=1_880_000_000_000_000,
            current_liabilities=1_650_000_000_000_000,
            total_debt=180_000_000_000_000,
            short_term_debt=60_000_000_000_000,
            long_term_debt=120_000_000_000_000,
            total_equity=290_000_000_000_000,
            retained_earnings=215_000_000_000_000,
            cfo=60_000_000_000_000,
            capex=10_500_000_000_000,
            fcf=49_500_000_000_000,
            dividends_paid=32_946_000_000_000,
            shares_outstanding=93_333_333_333
        )
        p2023_bmri = FinancialPeriod(
            year=2023,
            revenue=147_200_000_000_000,
            gross_profit=124_000_000_000_000,
            operating_profit=68_000_000_000_000,
            ebit=68_000_000_000_000,
            ebitda=72_500_000_000_000,
            net_income=55_060_000_000_000,
            eps=589.92,
            total_assets=2_020_000_000_000_000,
            current_assets=580_000_000_000_000,
            cash_and_equivalents=215_000_000_000_000,
            inventory=0.0,
            receivables=35_000_000_000_000,
            total_liabilities=1_755_000_000_000_000,
            current_liabilities=1_540_000_000_000_000,
            total_debt=170_000_000_000_000,
            short_term_debt=55_000_000_000_000,
            long_term_debt=115_000_000_000_000,
            total_equity=265_000_000_000_000,
            retained_earnings=195_000_000_000_000,
            cfo=56_000_000_000_000,
            capex=9_800_000_000_000,
            fcf=46_200_000_000_000,
            dividends_paid=30_000_000_000_000,
            shares_outstanding=93_333_333_333
        )
        p2022_bmri = FinancialPeriod(
            year=2022,
            revenue=128_500_000_000_000,
            gross_profit=108_000_000_000_000,
            operating_profit=51_200_000_000_000,
            ebit=51_200_000_000_000,
            ebitda=55_000_000_000_000,
            net_income=41_170_000_000_000,
            eps=441.10,
            total_assets=1_850_000_000_000_000,
            current_assets=520_000_000_000_000,
            cash_and_equivalents=190_000_000_000_000,
            inventory=0.0,
            receivables=30_000_000_000_000,
            total_liabilities=1_610_000_000_000_000,
            current_liabilities=1_420_000_000_000_000,
            total_debt=155_000_000_000_000,
            short_term_debt=50_000_000_000_000,
            long_term_debt=105_000_000_000_000,
            total_equity=240_000_000_000_000,
            retained_earnings=175_000_000_000_000,
            cfo=48_000_000_000_000,
            capex=8_500_000_000_000,
            fcf=39_500_000_000_000,
            dividends_paid=24_500_000_000_000,
            shares_outstanding=93_333_333_333
        )
        p2021_bmri = FinancialPeriod(
            year=2021,
            revenue=115_000_000_000_000,
            gross_profit=96_000_000_000_000,
            operating_profit=35_400_000_000_000,
            ebit=35_400_000_000_000,
            ebitda=39_000_000_000_000,
            net_income=28_030_000_000_000,
            eps=300.32,
            total_assets=1_725_000_000_000_000,
            current_assets=480_000_000_000_000,
            cash_and_equivalents=175_000_000_000_000,
            inventory=0.0,
            receivables=26_000_000_000_000,
            total_liabilities=1_510_000_000_000_000,
            current_liabilities=1_330_000_000_000_000,
            total_debt=140_000_000_000_000,
            short_term_debt=45_000_000_000_000,
            long_term_debt=95_000_000_000_000,
            total_equity=215_000_000_000_000,
            retained_earnings=155_000_000_000_000,
            cfo=40_000_000_000_000,
            capex=7_800_000_000_000,
            fcf=32_200_000_000_000,
            dividends_paid=16_500_000_000_000,
            shares_outstanding=93_333_333_333
        )

        data["BMRI"] = RawKeyStats(
            ticker="BMRI",
            name="Bank Mandiri (Persero) Tbk",
            sector="Financials",
            industry="Banking",
            current_price=6400.0,
            shares_outstanding=93_333_333_333,
            market_cap=597_333_333_331_200,
            dps=353.0,
            beta=1.18,
            pe_mean_5y=11.8,
            pe_standard_deviation=1.8,
            pbv_mean_5y=2.1,
            pbv_standard_deviation=0.25,
            is_syariah=False,
            current_period=p2024_bmri,
            previous_period=p2023_bmri,
            historical_periods=[p2023_bmri, p2022_bmri, p2021_bmri],
            bank_metrics=BankSpecificMetrics(
                car=22.4,
                npl_gross=1.12,
                npl_net=0.35,
                nim=5.45,
                bopo=56.2,
                ldr=89.5,
                casa=79.4,
                cost_of_credit=1.1
            )
        )

        # -------------------------------------------------------------
        # 4. ASII (Astra International) - Conglomerate / Value Moat
        # -------------------------------------------------------------
        p2024_asii = FinancialPeriod(
            year=2024,
            revenue=318_000_000_000_000,
            gross_profit=68_500_000_000_000,
            operating_profit=42_800_000_000_000,
            ebit=42_800_000_000_000,
            ebitda=55_000_000_000_000,
            net_income=33_800_000_000_000,
            eps=834.90,
            total_assets=455_000_000_000_000,
            current_assets=185_000_000_000_000,
            cash_and_equivalents=52_000_000_000_000,
            inventory=32_000_000_000_000,
            receivables=78_000_000_000_000,
            total_liabilities=205_000_000_000_000,
            current_liabilities=135_000_000_000_000,
            total_debt=95_000_000_000_000,
            short_term_debt=45_000_000_000_000,
            long_term_debt=50_000_000_000_000,
            total_equity=250_000_000_000_000,
            retained_earnings=195_000_000_000_000,
            cfo=41_000_000_000_000,
            capex=18_000_000_000_000,
            fcf=23_000_000_000_000,
            dividends_paid=21_010_000_000_000,
            shares_outstanding=40_483_553_140
        )
        p2023_asii = FinancialPeriod(
            year=2023,
            revenue=316_565_000_000_000,
            gross_profit=67_200_000_000_000,
            operating_profit=43_500_000_000_000,
            ebit=43_500_000_000_000,
            ebitda=54_800_000_000_000,
            net_income=33_839_000_000_000,
            eps=835.87,
            total_assets=445_000_000_000_000,
            current_assets=178_000_000_000_000,
            cash_and_equivalents=48_000_000_000_000,
            inventory=31_000_000_000_000,
            receivables=75_000_000_000_000,
            total_liabilities=198_000_000_000_000,
            current_liabilities=130_000_000_000_000,
            total_debt=92_000_000_000_000,
            short_term_debt=42_000_000_000_000,
            long_term_debt=50_000_000_000_000,
            total_equity=247_000_000_000_000,
            retained_earnings=188_000_000_000_000,
            cfo=39_500_000_000_000,
            capex=17_500_000_000_000,
            fcf=22_000_000_000_000,
            dividends_paid=20_500_000_000_000,
            shares_outstanding=40_483_553_140
        )
        p2022_asii = FinancialPeriod(
            year=2022,
            revenue=301_379_000_000_000,
            gross_profit=64_100_000_000_000,
            operating_profit=39_200_000_000_000,
            ebit=39_200_000_000_000,
            ebitda=49_500_000_000_000,
            net_income=28_944_000_000_000,
            eps=714.86,
            total_assets=413_000_000_000_000,
            current_assets=165_000_000_000_000,
            cash_and_equivalents=43_000_000_000_000,
            inventory=28_000_000_000_000,
            receivables=68_000_000_000_000,
            total_liabilities=189_000_000_000_000,
            current_liabilities=122_000_000_000_000,
            total_debt=88_000_000_000_000,
            short_term_debt=40_000_000_000_000,
            long_term_debt=48_000_000_000_000,
            total_equity=224_000_000_000_000,
            retained_earnings=172_000_000_000_000,
            cfo=36_000_000_000_000,
            capex=15_000_000_000_000,
            fcf=21_000_000_000_000,
            dividends_paid=16_200_000_000_000,
            shares_outstanding=40_483_553_140
        )
        p2021_asii = FinancialPeriod(
            year=2021,
            revenue=233_485_000_000_000,
            gross_profit=49_500_000_000_000,
            operating_profit=27_800_000_000_000,
            ebit=27_800_000_000_000,
            ebitda=36_000_000_000_000,
            net_income=20_196_000_000_000,
            eps=498.97,
            total_assets=367_000_000_000_000,
            current_assets=142_000_000_000_000,
            cash_and_equivalents=38_000_000_000_000,
            inventory=24_000_000_000_000,
            receivables=58_000_000_000_000,
            total_liabilities=165_000_000_000_000,
            current_liabilities=108_000_000_000_000,
            total_debt=82_000_000_000_000,
            short_term_debt=38_000_000_000_000,
            long_term_debt=44_000_000_000_000,
            total_equity=202_000_000_000_000,
            retained_earnings=156_000_000_000_000,
            cfo=30_000_000_000_000,
            capex=11_500_000_000_000,
            fcf=18_500_000_000_000,
            dividends_paid=10_500_000_000_000,
            shares_outstanding=40_483_553_140
        )

        data["ASII"] = RawKeyStats(
            ticker="ASII",
            name="Astra International Tbk",
            sector="Industrials",
            industry="Automotive & Conglomerate",
            current_price=5100.0,
            shares_outstanding=40_483_553_140,
            market_cap=206_466_121_014_000,
            dps=519.0,
            beta=0.95,
            pe_mean_5y=8.8,
            pe_standard_deviation=1.5,
            pbv_mean_5y=1.25,
            pbv_standard_deviation=0.2,
            is_syariah=False,
            current_period=p2024_asii,
            previous_period=p2023_asii,
            historical_periods=[p2023_asii, p2022_asii, p2021_asii]
        )

        # -------------------------------------------------------------
        # 5. ADRO (Adaro Energy) - Dividend Cash Cow & Coal/Renewable
        # -------------------------------------------------------------
        p2024_adro = FinancialPeriod(
            year=2024,
            revenue=98_000_000_000_000,
            gross_profit=42_000_000_000_000,
            operating_profit=32_500_000_000_000,
            ebit=32_500_000_000_000,
            ebitda=39_000_000_000_000,
            net_income=24_500_000_000_000,
            eps=765.96,
            total_assets=160_000_000_000_000,
            current_assets=72_000_000_000_000,
            cash_and_equivalents=48_000_000_000_000,
            inventory=6_500_000_000_000,
            receivables=9_500_000_000_000,
            total_liabilities=52_000_000_000_000,
            current_liabilities=31_000_000_000_000,
            total_debt=22_000_000_000_000,
            short_term_debt=8_000_000_000_000,
            long_term_debt=14_000_000_000_000,
            total_equity=108_000_000_000_000,
            retained_earnings=85_000_000_000_000,
            cfo=29_000_000_000_000,
            capex=8_200_000_000_000,
            fcf=20_800_000_000_000,
            dividends_paid=13_114_000_000_000,
            shares_outstanding=31_985_962_000
        )
        p2023_adro = FinancialPeriod(
            year=2023,
            revenue=102_000_000_000_000,
            gross_profit=46_000_000_000_000,
            operating_profit=36_000_000_000_000,
            ebit=36_000_000_000_000,
            ebitda=43_000_000_000_000,
            net_income=26_800_000_000_000,
            eps=837.86,
            total_assets=162_000_000_000_000,
            current_assets=75_000_000_000_000,
            cash_and_equivalents=51_000_000_000_000,
            inventory=6_200_000_000_000,
            receivables=10_000_000_000_000,
            total_liabilities=55_000_000_000_000,
            current_liabilities=33_000_000_000_000,
            total_debt=24_000_000_000_000,
            short_term_debt=9_000_000_000_000,
            long_term_debt=15_000_000_000_000,
            total_equity=107_000_000_000_000,
            retained_earnings=82_000_000_000_000,
            cfo=31_000_000_000_000,
            capex=7_800_000_000_000,
            fcf=23_200_000_000_000,
            dividends_paid=14_000_000_000_000,
            shares_outstanding=31_985_962_000
        )
        p2022_adro = FinancialPeriod(
            year=2022,
            revenue=110_200_000_000_000,
            gross_profit=58_000_000_000_000,
            operating_profit=48_500_000_000_000,
            ebit=48_500_000_000_000,
            ebitda=56_000_000_000_000,
            net_income=38_600_000_000_000,
            eps=1206.78,
            total_assets=165_000_000_000_000,
            current_assets=78_000_000_000_000,
            cash_and_equivalents=55_000_000_000_000,
            inventory=5_800_000_000_000,
            receivables=11_000_000_000_000,
            total_liabilities=58_000_000_000_000,
            current_liabilities=35_000_000_000_000,
            total_debt=26_000_000_000_000,
            short_term_debt=10_000_000_000_000,
            long_term_debt=16_000_000_000_000,
            total_equity=107_000_000_000_000,
            retained_earnings=78_000_000_000_000,
            cfo=42_000_000_000_000,
            capex=8_000_000_000_000,
            fcf=34_000_000_000_000,
            dividends_paid=15_500_000_000_000,
            shares_outstanding=31_985_962_000
        )
        p2021_adro = FinancialPeriod(
            year=2021,
            revenue=57_100_000_000_000,
            gross_profit=25_400_000_000_000,
            operating_profit=18_200_000_000_000,
            ebit=18_200_000_000_000,
            ebitda=22_000_000_000_000,
            net_income=14_700_000_000_000,
            eps=459.57,
            total_assets=112_000_000_000_000,
            current_assets=48_000_000_000_000,
            cash_and_equivalents=28_000_000_000_000,
            inventory=4_200_000_000_000,
            receivables=8_000_000_000_000,
            total_liabilities=42_000_000_000_000,
            current_liabilities=24_000_000_000_000,
            total_debt=22_000_000_000_000,
            short_term_debt=8_000_000_000_000,
            long_term_debt=14_000_000_000_000,
            total_equity=70_000_000_000_000,
            retained_earnings=52_000_000_000_000,
            cfo=21_000_000_000_000,
            capex=4_500_000_000_000,
            fcf=16_500_000_000_000,
            dividends_paid=6_200_000_000_000,
            shares_outstanding=31_985_962_000
        )

        data["ADRO"] = RawKeyStats(
            ticker="ADRO",
            name="Alamtri Resources Indonesia Tbk (Adaro)",
            sector="Energy",
            industry="Coal & Energy",
            current_price=3650.0,
            shares_outstanding=31_985_962_000,
            market_cap=116_748_761_300_000,
            dps=410.0,
            beta=1.35,
            pe_mean_5y=4.8,
            pe_standard_deviation=1.2,
            pbv_mean_5y=0.95,
            pbv_standard_deviation=0.2,
            is_syariah=True,
            current_period=p2024_adro,
            previous_period=p2023_adro,
            historical_periods=[p2023_adro, p2022_adro, p2021_adro]
        )

        # -------------------------------------------------------------
        # 6. ICBP (Indofood CBP Sukses Makmur) - Consumer Goods Moat
        # -------------------------------------------------------------
        p2024_icbp = FinancialPeriod(
            year=2024,
            revenue=71_500_000_000_000,
            gross_profit=26_200_000_000_000,
            operating_profit=15_800_000_000_000,
            ebit=15_800_000_000_000,
            ebitda=18_500_000_000_000,
            net_income=9_600_000_000_000,
            eps=823.19,
            total_assets=124_000_000_000_000,
            current_assets=42_000_000_000_000,
            cash_and_equivalents=16_500_000_000_000,
            inventory=8_500_000_000_000,
            receivables=11_000_000_000_000,
            total_liabilities=62_000_000_000_000,
            current_liabilities=24_000_000_000_000,
            total_debt=44_000_000_000_000,
            short_term_debt=8_000_000_000_000,
            long_term_debt=36_000_000_000_000,
            total_equity=62_000_000_000_000,
            retained_earnings=45_000_000_000_000,
            cfo=14_200_000_000_000,
            capex=4_200_000_000_000,
            fcf=10_000_000_000_000,
            dividends_paid=2_740_000_000_000,
            shares_outstanding=11_661_908_000
        )
        p2023_icbp = FinancialPeriod(
            year=2023,
            revenue=67_900_000_000_000,
            gross_profit=24_800_000_000_000,
            operating_profit=14_400_000_000_000,
            ebit=14_400_000_000_000,
            ebitda=16_800_000_000_000,
            net_income=6_990_000_000_000,
            eps=599.39,
            total_assets=119_000_000_000_000,
            current_assets=39_500_000_000_000,
            cash_and_equivalents=15_200_000_000_000,
            inventory=8_100_000_000_000,
            receivables=10_200_000_000_000,
            total_liabilities=60_000_000_000_000,
            current_liabilities=23_000_000_000_000,
            total_debt=43_000_000_000_000,
            short_term_debt=7_500_000_000_000,
            long_term_debt=35_500_000_000_000,
            total_equity=59_000_000_000_000,
            retained_earnings=42_000_000_000_000,
            cfo=12_800_000_000_000,
            capex=3_900_000_000_000,
            fcf=8_900_000_000_000,
            dividends_paid=2_400_000_000_000,
            shares_outstanding=11_661_908_000
        )
        p2022_icbp = FinancialPeriod(
            year=2022,
            revenue=64_800_000_000_000,
            gross_profit=21_500_000_000_000,
            operating_profit=13_200_000_000_000,
            ebit=13_200_000_000_000,
            ebitda=15_200_000_000_000,
            net_income=4_590_000_000_000,
            eps=393.59,
            total_assets=115_000_000_000_000,
            current_assets=36_000_000_000_000,
            cash_and_equivalents=13_800_000_000_000,
            inventory=7_600_000_000_000,
            receivables=9_500_000_000_000,
            total_liabilities=58_000_000_000_000,
            current_liabilities=22_000_000_000_000,
            total_debt=42_000_000_000_000,
            short_term_debt=7_000_000_000_000,
            long_term_debt=35_000_000_000_000,
            total_equity=57_000_000_000_000,
            retained_earnings=39_500_000_000_000,
            cfo=11_200_000_000_000,
            capex=3_600_000_000_000,
            fcf=7_600_000_000_000,
            dividends_paid=2_200_000_000_000,
            shares_outstanding=11_661_908_000
        )
        p2021_icbp = FinancialPeriod(
            year=2021,
            revenue=56_800_000_000_000,
            gross_profit=19_200_000_000_000,
            operating_profit=11_800_000_000_000,
            ebit=11_800_000_000_000,
            ebitda=13_500_000_000_000,
            net_income=6_390_000_000_000,
            eps=547.94,
            total_assets=103_000_000_000_000,
            current_assets=32_000_000_000_000,
            cash_and_equivalents=12_000_000_000_000,
            inventory=6_800_000_000_000,
            receivables=8_200_000_000_000,
            total_liabilities=52_000_000_000_000,
            current_liabilities=19_500_000_000_000,
            total_debt=38_000_000_000_000,
            short_term_debt=6_000_000_000_000,
            long_term_debt=32_000_000_000_000,
            total_equity=51_000_000_000_000,
            retained_earnings=36_000_000_000_000,
            cfo=9_800_000_000_000,
            capex=3_200_000_000_000,
            fcf=6_600_000_000_000,
            dividends_paid=2_000_000_000_000,
            shares_outstanding=11_661_908_000
        )

        data["ICBP"] = RawKeyStats(
            ticker="ICBP",
            name="Indofood CBP Sukses Makmur Tbk",
            sector="Consumer Non-Cyclicals",
            industry="Packaged Food & FMCG",
            current_price=11750.0,
            shares_outstanding=11_661_908_000,
            market_cap=137_027_419_000_000,
            dps=235.0,
            beta=0.65,
            pe_mean_5y=16.5,
            pe_standard_deviation=2.0,
            pbv_mean_5y=2.8,
            pbv_standard_deviation=0.3,
            is_syariah=True,
            current_period=p2024_icbp,
            previous_period=p2023_icbp,
            historical_periods=[p2023_icbp, p2022_icbp, p2021_icbp]
        )

        # -------------------------------------------------------------
        # 7. TLKM (Telkom Indonesia) - Telecom Utility Cash Flow
        # -------------------------------------------------------------
        p2024_tlkm = FinancialPeriod(
            year=2024,
            revenue=153_000_000_000_000,
            gross_profit=51_000_000_000_000,
            operating_profit=44_000_000_000_000,
            ebit=44_000_000_000_000,
            ebitda=78_000_000_000_000,
            net_income=24_500_000_000_000,
            eps=247.31,
            total_assets=298_000_000_000_000,
            current_assets=58_000_000_000_000,
            cash_and_equivalents=29_000_000_000_000,
            inventory=1_200_000_000_000,
            receivables=16_000_000_000_000,
            total_liabilities=142_000_000_000_000,
            current_liabilities=76_000_000_000_000,
            total_debt=68_000_000_000_000,
            short_term_debt=22_000_000_000_000,
            long_term_debt=46_000_000_000_000,
            total_equity=156_000_000_000_000,
            retained_earnings=112_000_000_000_000,
            cfo=56_000_000_000_000,
            capex=31_000_000_000_000,
            fcf=25_000_000_000_000,
            dividends_paid=17_633_000_000_000,
            shares_outstanding=99_062_216_600
        )
        p2023_tlkm = FinancialPeriod(
            year=2023,
            revenue=149_216_000_000_000,
            gross_profit=49_800_000_000_000,
            operating_profit=44_500_000_000_000,
            ebit=44_500_000_000_000,
            ebitda=77_600_000_000_000,
            net_income=24_560_000_000_000,
            eps=247.92,
            total_assets=287_000_000_000_000,
            current_assets=54_000_000_000_000,
            cash_and_equivalents=28_000_000_000_000,
            inventory=1_100_000_000_000,
            receivables=15_200_000_000_000,
            total_liabilities=138_000_000_000_000,
            current_liabilities=72_000_000_000_000,
            total_debt=65_000_000_000_000,
            short_term_debt=20_000_000_000_000,
            long_term_debt=45_000_000_000_000,
            total_equity=149_000_000_000_000,
            retained_earnings=105_000_000_000_000,
            cfo=54_000_000_000_000,
            capex=30_000_000_000_000,
            fcf=24_000_000_000_000,
            dividends_paid=16_800_000_000_000,
            shares_outstanding=99_062_216_600
        )
        p2022_tlkm = FinancialPeriod(
            year=2022,
            revenue=147_306_000_000_000,
            gross_profit=48_200_000_000_000,
            operating_profit=39_600_000_000_000,
            ebit=39_600_000_000_000,
            ebitda=72_000_000_000_000,
            net_income=20_753_000_000_000,
            eps=209.46,
            total_assets=275_000_000_000_000,
            current_assets=50_000_000_000_000,
            cash_and_equivalents=26_000_000_000_000,
            inventory=1_000_000_000_000,
            receivables=14_500_000_000_000,
            total_liabilities=132_000_000_000_000,
            current_liabilities=68_000_000_000_000,
            total_debt=62_000_000_000_000,
            short_term_debt=18_000_000_000_000,
            long_term_debt=44_000_000_000_000,
            total_equity=143_000_000_000_000,
            retained_earnings=98_000_000_000_000,
            cfo=50_000_000_000_000,
            capex=28_500_000_000_000,
            fcf=21_500_000_000_000,
            dividends_paid=15_500_000_000_000,
            shares_outstanding=99_062_216_600
        )
        p2021_tlkm = FinancialPeriod(
            year=2021,
            revenue=143_210_000_000_000,
            gross_profit=47_100_000_000_000,
            operating_profit=47_600_000_000_000,
            ebit=47_600_000_000_000,
            ebitda=75_000_000_000_000,
            net_income=24_760_000_000_000,
            eps=249.94,
            total_assets=277_000_000_000_000,
            current_assets=52_000_000_000_000,
            cash_and_equivalents=27_000_000_000_000,
            inventory=900_000_000_000,
            receivables=13_800_000_000_000,
            total_liabilities=131_000_000_000_000,
            current_liabilities=67_000_000_000_000,
            total_debt=60_000_000_000_000,
            short_term_debt=17_000_000_000_000,
            long_term_debt=43_000_000_000_000,
            total_equity=146_000_000_000_000,
            retained_earnings=95_000_000_000_000,
            cfo=52_000_000_000_000,
            capex=28_000_000_000_000,
            fcf=24_000_000_000_000,
            dividends_paid=16_000_000_000_000,
            shares_outstanding=99_062_216_600
        )

        data["TLKM"] = RawKeyStats(
            ticker="TLKM",
            name="Telkom Indonesia (Persero) Tbk",
            sector="Telecommunication",
            industry="Wireless & Fixed Broadband",
            current_price=2890.0,
            shares_outstanding=99_062_216_600,
            market_cap=286_289_806_000_000,
            dps=178.0,
            beta=0.88,
            pe_mean_5y=15.0,
            pe_standard_deviation=2.2,
            pbv_mean_5y=2.9,
            pbv_standard_deviation=0.4,
            is_syariah=True,
            current_period=p2024_tlkm,
            previous_period=p2023_tlkm,
            historical_periods=[p2023_tlkm, p2022_tlkm, p2021_tlkm]
        )

        # -------------------------------------------------------------
        # 8. UNTR (United Tractors) - Heavy Equipment & Mining
        # -------------------------------------------------------------
        p2024_untr = FinancialPeriod(
            year=2024,
            revenue=132_000_000_000_000,
            gross_profit=32_000_000_000_000,
            operating_profit=24_500_000_000_000,
            ebit=24_500_000_000_000,
            ebitda=33_000_000_000_000,
            net_income=19_200_000_000_000,
            eps=5147.26,
            total_assets=154_000_000_000_000,
            current_assets=72_000_000_000_000,
            cash_and_equivalents=24_000_000_000_000,
            inventory=18_000_000_000_000,
            receivables=22_000_000_000_000,
            total_liabilities=64_000_000_000_000,
            current_liabilities=48_000_000_000_000,
            total_debt=18_000_000_000_000,
            short_term_debt=8_000_000_000_000,
            long_term_debt=10_000_000_000_000,
            total_equity=90_000_000_000_000,
            retained_earnings=78_000_000_000_000,
            cfo=24_000_000_000_000,
            capex=12_000_000_000_000,
            fcf=12_000_000_000_000,
            dividends_paid=8_467_000_000_000,
            shares_outstanding=3_730_135_136
        )
        p2023_untr = FinancialPeriod(
            year=2023,
            revenue=128_800_000_000_000,
            gross_profit=33_200_000_000_000,
            operating_profit=26_000_000_000_000,
            ebit=26_000_000_000_000,
            ebitda=34_500_000_000_000,
            net_income=20_610_000_000_000,
            eps=5525.27,
            total_assets=148_000_000_000_000,
            current_assets=68_000_000_000_000,
            cash_and_equivalents=22_000_000_000_000,
            inventory=17_500_000_000_000,
            receivables=20_500_000_000_000,
            total_liabilities=62_000_000_000_000,
            current_liabilities=46_000_000_000_000,
            total_debt=17_000_000_000_000,
            short_term_debt=7_500_000_000_000,
            long_term_debt=9_500_000_000_000,
            total_equity=86_000_000_000_000,
            retained_earnings=74_000_000_000_000,
            cfo=25_000_000_000_000,
            capex=11_500_000_000_000,
            fcf=13_500_000_000_000,
            dividends_paid=8_000_000_000_000,
            shares_outstanding=3_730_135_136
        )
        p2022_untr = FinancialPeriod(
            year=2022,
            revenue=123_600_000_000_000,
            gross_profit=34_800_000_000_000,
            operating_profit=27_200_000_000_000,
            ebit=27_200_000_000_000,
            ebitda=35_000_000_000_000,
            net_income=21_000_000_000_000,
            eps=5629.82,
            total_assets=140_000_000_000_000,
            current_assets=64_000_000_000_000,
            cash_and_equivalents=20_000_000_000_000,
            inventory=16_000_000_000_000,
            receivables=19_000_000_000_000,
            total_liabilities=58_000_000_000_000,
            current_liabilities=42_000_000_000_000,
            total_debt=16_000_000_000_000,
            short_term_debt=7_000_000_000_000,
            long_term_debt=9_000_000_000_000,
            total_equity=82_000_000_000_000,
            retained_earnings=70_000_000_000_000,
            cfo=26_000_000_000_000,
            capex=10_000_000_000_000,
            fcf=16_000_000_000_000,
            dividends_paid=7_500_000_000_000,
            shares_outstanding=3_730_135_136
        )
        p2021_untr = FinancialPeriod(
            year=2021,
            revenue=79_500_000_000_000,
            gross_profit=18_200_000_000_000,
            operating_profit=13_800_000_000_000,
            ebit=13_800_000_000_000,
            ebitda=18_000_000_000_000,
            net_income=10_280_000_000_000,
            eps=2755.93,
            total_assets=112_000_000_000_000,
            current_assets=50_000_000_000_000,
            cash_and_equivalents=16_000_000_000_000,
            inventory=11_000_000_000_000,
            receivables=14_000_000_000_000,
            total_liabilities=41_000_000_000_000,
            current_liabilities=30_000_000_000_000,
            total_debt=12_000_000_000_000,
            short_term_debt=5_000_000_000_000,
            long_term_debt=7_000_000_000_000,
            total_equity=71_000_000_000_000,
            retained_earnings=60_000_000_000_000,
            cfo=15_000_000_000_000,
            capex=6_500_000_000_000,
            fcf=8_500_000_000_000,
            dividends_paid=3_800_000_000_000,
            shares_outstanding=3_730_135_136
        )

        data["UNTR"] = RawKeyStats(
            ticker="UNTR",
            name="United Tractors Tbk",
            sector="Industrials",
            industry="Heavy Equipment & Mining Services",
            current_price=26800.0,
            shares_outstanding=3_730_135_136,
            market_cap=99_967_621_644_800,
            dps=2270.0,
            beta=1.1,
            pe_mean_5y=5.8,
            pe_standard_deviation=1.1,
            pbv_mean_5y=1.1,
            pbv_standard_deviation=0.2,
            is_syariah=True,
            current_period=p2024_untr,
            previous_period=p2023_untr,
            historical_periods=[p2023_untr, p2022_untr, p2021_untr]
        )

        # -------------------------------------------------------------
        # 9. KLBF (Kalbe Farma) - Healthcare & Pharma Leader
        # -------------------------------------------------------------
        p2024_klbf = FinancialPeriod(
            year=2024,
            revenue=32_000_000_000_000,
            gross_profit=13_200_000_000_000,
            operating_profit=4_400_000_000_000,
            ebit=4_400_000_000_000,
            ebitda=5_200_000_000_000,
            net_income=3_250_000_000_000,
            eps=69.33,
            total_assets=28_500_000_000_000,
            current_assets=18_200_000_000_000,
            cash_and_equivalents=5_200_000_000_000,
            inventory=6_100_000_000_000,
            receivables=5_400_000_000_000,
            total_liabilities=5_600_000_000_000,
            current_liabilities=4_100_000_000_000,
            total_debt=1_200_000_000_000,
            short_term_debt=800_000_000_000,
            long_term_debt=400_000_000_000,
            total_equity=22_900_000_000_000,
            retained_earnings=19_800_000_000_000,
            cfo=3_800_000_000_000,
            capex=1_100_000_000_000,
            fcf=2_700_000_000_000,
            dividends_paid=2_015_000_000_000,
            shares_outstanding=46_875_122_110
        )
        p2023_klbf = FinancialPeriod(
            year=2023,
            revenue=30_447_000_000_000,
            gross_profit=12_400_000_000_000,
            operating_profit=3_800_000_000_000,
            ebit=3_800_000_000_000,
            ebitda=4_600_000_000_000,
            net_income=2_770_000_000_000,
            eps=59.09,
            total_assets=27_200_000_000_000,
            current_assets=17_100_000_000_000,
            cash_and_equivalents=4_800_000_000_000,
            inventory=5_800_000_000_000,
            receivables=5_100_000_000_000,
            total_liabilities=5_300_000_000_000,
            current_liabilities=3_900_000_000_000,
            total_debt=1_100_000_000_000,
            short_term_debt=750_000_000_000,
            long_term_debt=350_000_000_000,
            total_equity=21_900_000_000_000,
            retained_earnings=18_700_000_000_000,
            cfo=3_400_000_000_000,
            capex=1_050_000_000_000,
            fcf=2_350_000_000_000,
            dividends_paid=1_800_000_000_000,
            shares_outstanding=46_875_122_110
        )
        p2022_klbf = FinancialPeriod(
            year=2022,
            revenue=28_910_000_000_000,
            gross_profit=11_900_000_000_000,
            operating_profit=4_200_000_000_000,
            ebit=4_200_000_000_000,
            ebitda=4_950_000_000_000,
            net_income=3_150_000_000_000,
            eps=67.20,
            total_assets=25_800_000_000_000,
            current_assets=16_000_000_000_000,
            cash_and_equivalents=4_500_000_000_000,
            inventory=5_400_000_000_000,
            receivables=4_800_000_000_000,
            total_liabilities=5_000_000_000_000,
            current_liabilities=3_700_000_000_000,
            total_debt=1_000_000_000_000,
            short_term_debt=700_000_000_000,
            long_term_debt=300_000_000_000,
            total_equity=20_800_000_000_000,
            retained_earnings=17_500_000_000_000,
            cfo=3_600_000_000_000,
            capex=1_000_000_000_000,
            fcf=2_600_000_000_000,
            dividends_paid=1_650_000_000_000,
            shares_outstanding=46_875_122_110
        )
        p2021_klbf = FinancialPeriod(
            year=2021,
            revenue=26_260_000_000_000,
            gross_profit=11_200_000_000_000,
            operating_profit=4_100_000_000_000,
            ebit=4_100_000_000_000,
            ebitda=4_800_000_000_000,
            net_income=3_180_000_000_000,
            eps=67.84,
            total_assets=24_500_000_000_000,
            current_assets=15_100_000_000_000,
            cash_and_equivalents=4_200_000_000_000,
            inventory=5_000_000_000_000,
            receivables=4_500_000_000_000,
            total_liabilities=4_800_000_000_000,
            current_liabilities=3_500_000_000_000,
            total_debt=950_000_000_000,
            short_term_debt=650_000_000_000,
            long_term_debt=300_000_000_000,
            total_equity=19_700_000_000_000,
            retained_earnings=16_400_000_000_000,
            cfo=3_500_000_000_000,
            capex=950_000_000_000,
            fcf=2_550_000_000_000,
            dividends_paid=1_500_000_000_000,
            shares_outstanding=46_875_122_110
        )

        data["KLBF"] = RawKeyStats(
            ticker="KLBF",
            name="Kalbe Farma Tbk",
            sector="Healthcare",
            industry="Pharmaceuticals & Health Products",
            current_price=1450.0,
            shares_outstanding=46_875_122_110,
            market_cap=67_968_927_059_500,
            dps=43.0,
            beta=0.72,
            pe_mean_5y=22.5,
            pe_standard_deviation=2.5,
            pbv_mean_5y=3.6,
            pbv_standard_deviation=0.4,
            is_syariah=True,
            current_period=p2024_klbf,
            previous_period=p2023_klbf,
            historical_periods=[p2023_klbf, p2022_klbf, p2021_klbf]
        )

        # -------------------------------------------------------------
        # 10. PTBA (Bukit Asam) - High Dividend Yield State Coal
        # -------------------------------------------------------------
        p2024_ptba = FinancialPeriod(
            year=2024,
            revenue=41_500_000_000_000,
            gross_profit=9_500_000_000_000,
            operating_profit=6_800_000_000_000,
            ebit=6_800_000_000_000,
            ebitda=8_900_000_000_000,
            net_income=5_100_000_000_000,
            eps=442.68,
            total_assets=41_000_000_000_000,
            current_assets=19_500_000_000_000,
            cash_and_equivalents=6_800_000_000_000,
            inventory=2_400_000_000_000,
            receivables=4_800_000_000_000,
            total_liabilities=18_500_000_000_000,
            current_liabilities=12_000_000_000_000,
            total_debt=4_500_000_000_000,
            short_term_debt=2_000_000_000_000,
            long_term_debt=2_500_000_000_000,
            total_equity=22_500_000_000_000,
            retained_earnings=16_500_000_000_000,
            cfo=6_200_000_000_000,
            capex=2_100_000_000_000,
            fcf=4_100_000_000_000,
            dividends_paid=4_573_000_000_000,
            shares_outstanding=11_520_659_250
        )
        p2023_ptba = FinancialPeriod(
            year=2023,
            revenue=38_500_000_000_000,
            gross_profit=10_800_000_000_000,
            operating_profit=7_900_000_000_000,
            ebit=7_900_000_000_000,
            ebitda=9_800_000_000_000,
            net_income=6_110_000_000_000,
            eps=530.35,
            total_assets=38_800_000_000_000,
            current_assets=18_000_000_000_000,
            cash_and_equivalents=6_200_000_000_000,
            inventory=2_200_000_000_000,
            receivables=4_500_000_000_000,
            total_liabilities=17_200_000_000_000,
            current_liabilities=11_200_000_000_000,
            total_debt=4_200_000_000_000,
            short_term_debt=1_800_000_000_000,
            long_term_debt=2_400_000_000_000,
            total_equity=21_600_000_000_000,
            retained_earnings=15_800_000_000_000,
            cfo=7_100_000_000_000,
            capex=1_900_000_000_000,
            fcf=5_200_000_000_000,
            dividends_paid=5_800_000_000_000,
            shares_outstanding=11_520_659_250
        )
        p2022_ptba = FinancialPeriod(
            year=2022,
            revenue=42_600_000_000_000,
            gross_profit=17_500_000_000_000,
            operating_profit=15_200_000_000_000,
            ebit=15_200_000_000_000,
            ebitda=17_500_000_000_000,
            net_income=12_560_000_000_000,
            eps=1090.22,
            total_assets=45_400_000_000_000,
            current_assets=24_000_000_000_000,
            cash_and_equivalents=11_000_000_000_000,
            inventory=2_800_000_000_000,
            receivables=6_200_000_000_000,
            total_liabilities=16_500_000_000_000,
            current_liabilities=10_800_000_000_000,
            total_debt=3_800_000_000_000,
            short_term_debt=1_600_000_000_000,
            long_term_debt=2_200_000_000_000,
            total_equity=28_900_000_000_000,
            retained_earnings=22_500_000_000_000,
            cfo=14_500_000_000_000,
            capex=2_400_000_000_000,
            fcf=12_100_000_000_000,
            dividends_paid=8_000_000_000_000,
            shares_outstanding=11_520_659_250
        )
        p2021_ptba = FinancialPeriod(
            year=2021,
            revenue=29_300_000_000_000,
            gross_profit=11_200_000_000_000,
            operating_profit=9_800_000_000_000,
            ebit=9_800_000_000_000,
            ebitda=11_800_000_000_000,
            net_income=7_910_000_000_000,
            eps=686.59,
            total_assets=36_100_000_000_000,
            current_assets=17_200_000_000_000,
            cash_and_equivalents=5_000_000_000_000,
            inventory=2_000_000_000_000,
            receivables=4_200_000_000_000,
            total_liabilities=11_900_000_000_000,
            current_liabilities=7_800_000_000_000,
            total_debt=3_200_000_000_000,
            short_term_debt=1_200_000_000_000,
            long_term_debt=2_000_000_000_000,
            total_equity=24_200_000_000_000,
            retained_earnings=18_500_000_000_000,
            cfo=8_500_000_000_000,
            capex=1_800_000_000_000,
            fcf=6_700_000_000_000,
            dividends_paid=3_600_000_000_000,
            shares_outstanding=11_520_659_250
        )

        data["PTBA"] = RawKeyStats(
            ticker="PTBA",
            name="Bukit Asam Tbk",
            sector="Energy",
            industry="Coal Mining",
            current_price=2620.0,
            shares_outstanding=11_520_659_250,
            market_cap=30_184_127_235_000,
            dps=397.0,
            beta=1.28,
            pe_mean_5y=5.2,
            pe_standard_deviation=1.4,
            pbv_mean_5y=1.35,
            pbv_standard_deviation=0.25,
            is_syariah=True,
            current_period=p2024_ptba,
            previous_period=p2023_ptba,
            historical_periods=[p2023_ptba, p2022_ptba, p2021_ptba]
        )

        return data
