"""
Mock & Seed Data Provider: Contains realistic IDX financial statements,
KeyStats, and sector metrics for high-speed offline analysis and testing.
"""

from typing import Optional, List, Dict
from app.data_providers.base import BaseDataProvider
from app.models.keystats import RawKeyStats, FinancialPeriod, BankSpecificMetrics


class MockDataProvider(BaseDataProvider):
    def __init__(self):
        self._dataset: Dict[str, RawKeyStats] = self._init_dataset()

    def get_keystats(self, ticker: str) -> Optional[RawKeyStats]:
        clean_ticker = ticker.upper().replace(".JK", "").strip()
        return self._dataset.get(clean_ticker)

    def list_all_tickers(self) -> List[str]:
        return list(self._dataset.keys())

    def search_tickers(self, query: str) -> List[RawKeyStats]:
        q = query.upper().strip()
        return [
            v for k, v in self._dataset.items()
            if q in k or q in v.name.upper() or q in v.sector.upper()
        ]

    def _init_dataset(self) -> Dict[str, RawKeyStats]:
        data: Dict[str, RawKeyStats] = {}

        # -------------------------------------------------------------
        # 1. BBRI (Bank Rakyat Indonesia) - Banking Giant
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
            ),
            previous_period=FinancialPeriod(
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
            ),
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
            current_period=FinancialPeriod(
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
            ),
            previous_period=FinancialPeriod(
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
            ),
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
            current_period=FinancialPeriod(
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
            ),
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
            current_period=FinancialPeriod(
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
            ),
            previous_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 5. ADRO (Adaro Energy) - Dividend Cash Cow & Coal/Renewable
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
            ),
            previous_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 6. ICBP (Indofood CBP Sukses Makmur) - Consumer Goods Moat
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 7. TLKM (Telkom Indonesia) - Telecom Utility Cash Flow
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 8. UNTR (United Tractors) - Heavy Equipment & Mining
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 9. KLBF (Kalbe Farma) - Healthcare & Pharma Leader
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
        )

        # -------------------------------------------------------------
        # 10. PTBA (Bukit Asam) - High Dividend Yield State Coal
        # -------------------------------------------------------------
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
            current_period=FinancialPeriod(
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
        )

        return data
