"""
Calendar Service: Curates, computes dynamic timelines, filters, and maps economic/corporate catalysts to affected IDX stocks.
"""

from typing import List, Optional, Dict
from datetime import datetime, date, timedelta

from app.models.calendar import (
    CalendarAgendaItem,
    ImpactedStockItem,
    ScenarioItem,
    SectorSensitivityItem,
    CalendarStats,
    CalendarResponse,
    ImpactLevel,
    MarketScope,
    EventCategory,
    MarketBias
)


class CalendarService:
    def __init__(self):
        pass

    def _get_base_dataset(self, reference_date: Optional[date] = None) -> List[Dict]:
        """
        Returns rich curated calendar events dynamically anchored around reference_date (defaults to today).
        This guarantees relative countdowns (Today, Tomorrow, Upcoming in N days) are always meaningful.
        """
        ref = reference_date or date.today()

        # Generate realistic date offsets relative to today
        # Days: -2 (Past), 0 (Today), 1 (Tomorrow), 3, 5, 7, 10, 14, 18, 22, 28, 35
        d_m2 = (ref - timedelta(days=2)).strftime("%Y-%m-%d")
        d_0 = ref.strftime("%Y-%m-%d")
        d_p1 = (ref + timedelta(days=1)).strftime("%Y-%m-%d")
        d_p3 = (ref + timedelta(days=3)).strftime("%Y-%m-%d")
        d_p5 = (ref + timedelta(days=5)).strftime("%Y-%m-%d")
        d_p7 = (ref + timedelta(days=7)).strftime("%Y-%m-%d")
        d_p10 = (ref + timedelta(days=10)).strftime("%Y-%m-%d")
        d_p14 = (ref + timedelta(days=14)).strftime("%Y-%m-%d")
        d_p18 = (ref + timedelta(days=18)).strftime("%Y-%m-%d")
        d_p22 = (ref + timedelta(days=22)).strftime("%Y-%m-%d")
        d_p28 = (ref + timedelta(days=28)).strftime("%Y-%m-%d")
        d_p35 = (ref + timedelta(days=35)).strftime("%Y-%m-%d")

        return [
            # 1. BI-Rate (Bank Indonesia RDG)
            {
                "id": "bi-rate-decision",
                "title": "Pengumuman Suku Bunga Acuan BI-Rate (RDG Bank Indonesia)",
                "country": "Indonesia",
                "country_code": "ID",
                "flag_emoji": "🇮🇩",
                "institution": "Bank Indonesia (BI)",
                "category": EventCategory.INTEREST_RATE,
                "category_label": "Suku Bunga & Moneter",
                "event_date": d_p1,
                "time_utc7": "14:00 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "6.25%",
                "forecast_val": "6.00%",
                "actual_val": None,
                "unit": "%",
                "summary": "Rapat Dewan Gubernur (RDG) Bank Indonesia menentukan arah suku bunga acuan (BI-Rate). Pemangkasan suku bunga menjadi katalis positif utama bagi pertumbuhan kredit perbankan, emiten properti, otomotif, serta meredakan beban bunga emiten berutang tinggi.",
                "transmission_mechanism": "Pemotongan BI-Rate menurunkan Cost of Funds (CoF) perbankan dan suku bunga pinjaman/KPR. Sektor properti & otomotif mendapatkan dorongan permintaan karena cicilan konsumen lebih terjangkau. Sebaliknya jika BI menaikkan suku bunga, margin laba perbankan tertekan sementara emiten properti mengalami perlambatan pra-penjualan.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="CASA yang kuat (>80%) memberikan fleksibilitas NIM terbaik saat siklus suku bunga melonggar."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Penurunan CoF mempercepat pemulihan margin kredit mikro dan meningkatkan kemampuan bayar debitur UMKM."
                    ),
                    ImpactedStockItem(
                        ticker="BMRI",
                        name="Bank Mandiri (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Pertumbuhan kredit korporasi terakselerasi dengan likuiditas yang lebih longgar."
                    ),
                    ImpactedStockItem(
                        ticker="BSDE",
                        name="Bumi Serpong Damai Tbk",
                        sector="Real Estate & Properti",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Suku bunga KPR yang lebih rendah mendongkrak target marketing sales hunian dan ruko."
                    ),
                    ImpactedStockItem(
                        ticker="CTRA",
                        name="Ciputra Development Tbk",
                        sector="Real Estate & Properti",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Portofolio residensial kelas menengah sangat elastis terhadap pelonggaran bunga KPR."
                    ),
                    ImpactedStockItem(
                        ticker="ASII",
                        name="Astra International Tbk",
                        sector="Consumer Discretionary / Otomotif",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Suku bunga kredit multifinance (ACC & TAF) turun, mendongkrak daya beli kendaraan roda empat & roda dua."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="BI Pangkas Suku Bunga (-25 bps ke 6.00%)",
                        condition="Aktual <= 6.00% (Dovish)",
                        ihsg_impact="Rally Positif (+0.8% s/d +1.5%) didorong sektor finansial, properti, dan konsumer.",
                        sector_impact="Properti & Bank Big Caps memimpin penguatan.",
                        favored_stocks=["BBCA", "BBRI", "BMRI", "BSDE", "CTRA", "ASII"],
                        pressured_stocks=["Emiten berorientasi instrumen pasar uang / deposito jangka pendek."]
                    ),
                    ScenarioItem(
                        scenario_name="BI Tahan Suku Bunga di 6.25%",
                        condition="Aktual = 6.25% (Netral)",
                        ihsg_impact="Konsolidasi Netral (-0.2% s/d +0.3%), pasar fokus pada stabilitas Rupiah.",
                        sector_impact="Pergerakan selektif pada emiten dengan dividen yield tinggi.",
                        favored_stocks=["BBCA", "TLKM"],
                        pressured_stocks=["BSDE", "CTRA"]
                    ),
                    ScenarioItem(
                        scenario_name="BI Kejutan Naikkan Suku Bunga (+25 bps ke 6.50%)",
                        condition="Aktual >= 6.50% (Hawkish Ekstrem)",
                        ihsg_impact="Koreksi Tajam IHSG (-1.0% s/d -2.0%) akibat kekhawatiran likuiditas ketat.",
                        sector_impact="Tekanan berat pada sektor Properti, Konstruksi, dan High-Leverage.",
                        favored_stocks=["Eksportir berpendapatan valas (ADRO, MEDC)"],
                        pressured_stocks=["BBRI", "BSDE", "CTRA", "WIKA", "PTPP"]
                    )
                ],
                "actionable_strategy": "Akumulasi bertahap pada Big 4 Banks (BBCA, BBRI, BMRI, BBNI) dan developer berneraca sehat (CTRA, BSDE) menjelang rilis jika probabilitas pemangkasan tinggi.",
                "is_tentative": False
            },

            # 2. US Federal Reserve FOMC Interest Rate Decision
            {
                "id": "us-fomc-rate-decision",
                "title": "Keputusan Suku Bunga US Fed Funds Rate (FOMC Meeting)",
                "country": "Amerika Serikat",
                "country_code": "US",
                "flag_emoji": "🇺🇸",
                "institution": "Federal Reserve (The Fed)",
                "category": EventCategory.INTEREST_RATE,
                "category_label": "Suku Bunga & Moneter",
                "event_date": d_p7,
                "time_utc7": "01:00 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "5.50%",
                "forecast_val": "5.25%",
                "actual_val": None,
                "unit": "%",
                "summary": "Keputusan suku bunga bank sentral AS (The Fed) adalah katalis makro global terpenting. Perubahan suku bunga The Fed mempengaruhi indeks Dolar AS (DXY), yield US Treasury 10Y, arus modal asing (foreign inflow/outflow) ke bursa negara berkembang termasuk IHSG, serta kurs Rupiah (USD/IDR).",
                "transmission_mechanism": "Jika The Fed memangkas suku bunga, yield US Treasury melemah sehingga selisih imbal hasil obligasi Indonesia (SUN 10Y) menjadi lebih menarik. Hal ini memicu foreign capital inflow masif ke saham-saham Blue Chip IHSG. Sebaliknya jika The Fed bersikap hawkish, Dolar AS menguat dan Rupiah melemah, menekan emiten importir bahan baku dan emiten berutang valas USD.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Penerima arus foreign inflow terbesar pertama di bursa IDX saat sentimen global risk-on."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Likuiditas global yang membaik menurunkan tekanan yield obligasi pemerintah yang dimiliki perseroan."
                    ),
                    ImpactedStockItem(
                        ticker="GOTO",
                        name="GoTo Gojek Tokopedia Tbk",
                        sector="Technology",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Saham teknologi berbasis valuasi pertumbuhan (growth stock) sangat sensitif terhadap penurunan global cost of equity / discount rate."
                    ),
                    ImpactedStockItem(
                        ticker="ICBP",
                        name="Indofood CBP Sukses Makmur Tbk",
                        sector="Consumer Non-Cyclicals",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Pelemahan Dolar AS mengurangi potensi kerugian selisih kurs (foreign exchange loss) dari utang obligasi valas Pinehill."
                    ),
                    ImpactedStockItem(
                        ticker="MEDC",
                        name="Medco Energi Internasional Tbk",
                        sector="Energy / Minyak & Gas",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Pelemahan Dolar AS biasanya mendongkrak harga minyak mentah global WTI & Brent."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Fed Pangkas Suku Bunga & Beri Panduan Dovish",
                        condition="Cut 25-50 bps + Dot Plot Melonggar",
                        ihsg_impact="IHSG Berpotensi Rally Kuat (+1.0% s/d +2.0%), Foreign Inflow Masif.",
                        sector_impact="Big Banks, Teknologi (GOTO), dan Konsumer Impor menguat tajam.",
                        favored_stocks=["BBCA", "BBRI", "BMRI", "GOTO", "ICBP", "TLKM"],
                        pressured_stocks=["Dolar Tunai (USD Cash)"]
                    ),
                    ScenarioItem(
                        scenario_name="Fed Tahan Suku Bunga Sesuai Ekspektasi",
                        condition="Hold 5.50% tapi nada pidato Powell Netral",
                        ihsg_impact="IHSG Volatil Flat (-0.3% s/d +0.4%), pergerakan intraday sideways.",
                        sector_impact="Sektor defensif (Telekomunikasi, Consumer Staples) cenderung stabil.",
                        favored_stocks=["TLKM", "ICBP"],
                        pressured_stocks=["Saham-saham High-Beta"]
                    ),
                    ScenarioItem(
                        scenario_name="Fed Hawkish (Batal Pangkas / Isyaratkan Tahan Lama)",
                        condition="Higher for Longer Warning",
                        ihsg_impact="IHSG Mengalami Tekanan Koreksi (-1.2% s/d -2.5%), Foreign Outflow.",
                        sector_impact="Tekanan pada Rupiah, saham teknologi, dan emiten berbeban utang USD tinggi.",
                        favored_stocks=["Eksportir Komoditas Murni (ADRO, PTBA, ITMG)"],
                        pressured_stocks=["GOTO", "ICBP", "INDF", "CPIN", "JPFA"]
                    )
                ],
                "actionable_strategy": "Manfaatkan volatilitas pre-FOMC untuk entry bertahap pada emiten berfundamental kokoh dengan valuasi terdiskon (BBRI, BMRI, ICBP). Amankan stop loss ketat pada saham teknologi beta tinggi.",
                "is_tentative": False
            },

            # 3. US CPI Inflation Data (US Consumer Price Index)
            {
                "id": "us-cpi-inflation",
                "title": "Rilis Data Inflasi Konsumen AS (US CPI YoY & MoM)",
                "country": "Amerika Serikat",
                "country_code": "US",
                "flag_emoji": "🇺🇸",
                "institution": "US Bureau of Labor Statistics (BLS)",
                "category": EventCategory.INFLATION_GDP,
                "category_label": "Inflasi & GDP",
                "event_date": d_p3,
                "time_utc7": "19:30 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "2.9%",
                "forecast_val": "2.6%",
                "actual_val": None,
                "unit": "% YoY",
                "summary": "Data inflasi AS (CPI & Core CPI) adalah kompas utama The Fed dalam menentukan kecepatan pelonggaran suku bunga. Angka inflasi yang melandai di bawah konsensus akan memperkuat optimisme 'soft landing' dan mempercepat penurunan Fed Rate.",
                "transmission_mechanism": "Inflasi AS yang lebih rendah dari perkiraan menekan imbal hasil US Treasury 10Y dan indeks Dolar (DXY). Rupiah menguat terhadap Dolar AS, yang menguntungkan emiten pengimpor bahan baku (gandum, kedelai, pakan ternak) seperti ICBP, INDF, CPIN, JPFA. Sebaliknya inflasi AS yang 'hot' (tinggi) memicu kekhawatiran 'stagflasi' dan capital outflow dari pasar modal negara berkembang.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="ICBP",
                        name="Indofood CBP Sukses Makmur Tbk",
                        sector="Consumer Non-Cyclicals",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Penguatan Rupiah menurunkan beban impor gandum (wheat) dan bahan baku kemasan."
                    ),
                    ImpactedStockItem(
                        ticker="INDF",
                        name="Indofood Sukses Makmur Tbk",
                        sector="Consumer Non-Cyclicals",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Divisi Bogasari diuntungkan oleh penurunan biaya bahan baku gandum impor."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Sentimen risk-on global mendorong aliran dana institusi asing masuk kembali."
                    ),
                    ImpactedStockItem(
                        ticker="KLBF",
                        name="Kalbe Farma Tbk",
                        sector="Healthcare / Farmasi",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason=">80% bahan baku obat aktif (API) diimpor dengan mata uang USD; penguatan rupiah melindungi margin kotor (GPM)."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Inflasi AS Melandai (<2.6% YoY)",
                        condition="Aktual < 2.6% (Cooling Down)",
                        ihsg_impact="Sentimen Sangat Bullish, Rupiah menguat ke bawah Rp 16.000/USD.",
                        sector_impact="Consumer Goods, Perbankan, dan Healthcare melaju kencang.",
                        favored_stocks=["ICBP", "INDF", "KLBF", "BBCA", "BBRI"],
                        pressured_stocks=["DXY / Valas USD"]
                    ),
                    ScenarioItem(
                        scenario_name="Inflasi AS 'Panas' Diatas Perkiraan (>2.9% YoY)",
                        condition="Aktual > 2.9% (Sticky Inflation)",
                        ihsg_impact="IHSG Terkoreksi, yield obligasi US 10Y melonjak naik.",
                        sector_impact="Sektor berbasis impor tertekan; komoditas defensif lebih stabil.",
                        favored_stocks=["ADRO", "MEDC"],
                        pressured_stocks=["ICBP", "KLBF", "GOTO", "ASII"]
                    )
                ],
                "actionable_strategy": "Bila inflasi AS diproyeksikan mendingin, pasang posisi buy on weakness pada emiten konsumen primer berfundamental kuat (ICBP, INDF, KLBF).",
                "is_tentative": False
            },

            # 4. Indonesia BPS Inflation (CPI)
            {
                "id": "id-bps-inflation",
                "title": "Rilis Data Inflasi Indonesia BPS (CPI Bulanan & Tahunan)",
                "country": "Indonesia",
                "country_code": "ID",
                "flag_emoji": "🇮🇩",
                "institution": "Badan Pusat Statistik (BPS)",
                "category": EventCategory.INFLATION_GDP,
                "category_label": "Inflasi & GDP",
                "event_date": d_p5,
                "time_utc7": "11:00 WIB",
                "impact_level": ImpactLevel.MEDIUM,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "2.13%",
                "forecast_val": "2.05%",
                "actual_val": None,
                "unit": "% YoY",
                "summary": "Badan Pusat Statistik merilis data inflasi Indeks Harga Konsumen (IHK). Inflasi yang terkendali dalam rentang target Bank Indonesia (1.5% - 3.5%) menjaga daya beli masyarakat kelas menengah ke bawah dan memberikan ruang longgar bagi kebijakan moneter BI.",
                "transmission_mechanism": "Inflasi pangan bergejolak (volatile food) yang terkendali menjaga anggaran belanja konsumsi rumah tangga (private consumption). Emiten ritel modern (AMRT, ACES, MAPI) dan produsen barang konsumsi (ICBP, MYOR, UNVR) menikmati stabilitas volume penjualan barang.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="ICBP",
                        name="Indofood CBP Sukses Makmur Tbk",
                        sector="Consumer Non-Cyclicals",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Daya beli konsumen yang stabil mempertahankan volume penjualan mi instan dan produk susu."
                    ),
                    ImpactedStockItem(
                        ticker="ASII",
                        name="Astra International Tbk",
                        sector="Consumer Discretionary",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Inflasi rendah menjaga disposable income rumah tangga untuk pembelian otomotif."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kualitas aset debitur mikro lebih terjaga saat harga bahan pokok terkendali."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Inflasi Terjaga di Kisaran 1.8% - 2.2%",
                        condition="Sesuai target sasaran BI 2.5% ± 1%",
                        ihsg_impact="Netral Positif (+0.2% s/d +0.5%), memberi ruang pemangkasan BI-Rate.",
                        sector_impact="Sektor Ritel dan Consumer Staples solid.",
                        favored_stocks=["ICBP", "ASII", "BBRI"],
                        pressured_stocks=[]
                    ),
                    ScenarioItem(
                        scenario_name="Lonjakan Inflasi Pangan (>3.5%)",
                        condition="Lonjakan harga beras/minyak goreng ekstrem",
                        ihsg_impact="Sentimen Negatif, kekhawatiran penurunan daya beli masyarakat bawah.",
                        sector_impact="Consumer Discretionary dan Ritel tertekan.",
                        favored_stocks=["Produsen CPO (AALI, TAPG, LSIP)"],
                        pressured_stocks=["ASII", "ACES", "MAPI"]
                    )
                ],
                "actionable_strategy": "Pantau komponen inflasi inti (core inflation); jika inflasi inti naik stabil, ini menandakan pemulihan daya beli riil yang sehat.",
                "is_tentative": False
            },

            # 5. US Non-Farm Payrolls (NFP) & Unemployment
            {
                "id": "us-non-farm-payrolls",
                "title": "Rilis Data Ketenagakerjaan AS (Non-Farm Payrolls & Unemployment)",
                "country": "Amerika Serikat",
                "country_code": "US",
                "flag_emoji": "🇺🇸",
                "institution": "US Bureau of Labor Statistics (BLS)",
                "category": EventCategory.TRADE_MACRO,
                "category_label": "Ketenagakerjaan & Makro",
                "event_date": d_p10,
                "time_utc7": "19:30 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "114K",
                "forecast_val": "165K",
                "actual_val": None,
                "unit": "Jobs",
                "summary": "Non-Farm Payrolls (NFP) mengukur penambahan tenaga kerja sektor non-pertanian AS. Menjadi barometer kesehatan ekonomi AS: jika terlalu lemah memicu kekhawatiran resesi AS (Sahm Rule), jika terlalu panas memperlambat pemotongan Fed Rate. Kondisi 'Goldilocks' (moderat) paling disukai pasar saham global.",
                "transmission_mechanism": "Pasar saham global dan IHSG menyukai pertumbuhan kerja moderat (tidak terlalu panas yang memicu inflasi upah, namun tidak anjlok yang menandakan resesi). Resesi AS akan memukul permintaan ekspor komoditas Indonesia (Batu Bara, Minyak, Nikel).",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="ADRO",
                        name="Adaro Energy Indonesia Tbk",
                        sector="Energy / Batu Bara",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Sensitif terhadap prospek aktivitas industri manufaktur dan kebutuhan energi global."
                    ),
                    ImpactedStockItem(
                        ticker="MEDC",
                        name="Medco Energi Internasional Tbk",
                        sector="Energy / Migas",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Pergerakan harga minyak mentah global WTI/Brent langsung merespons prospek konsumsi energi AS."
                    ),
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Stabilitas ekonomi global memicu risk appetite investor asing masuk ke bursa emerging market."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Kondisi 'Goldilocks' (130K - 170K Penambahan Pekerjaan)",
                        condition="Pertumbuhan stabil, upah moderat",
                        ihsg_impact="IHSG Positif Terangkat (+0.5% s/d +1.0%), optimisme soft-landing.",
                        sector_impact="Seluruh sektor menguat merata (Broad-based rally).",
                        favored_stocks=["BBCA", "BBRI", "BMRI", "TLKM", "ASII"],
                        pressured_stocks=[]
                    ),
                    ScenarioItem(
                        scenario_name="Data Sangat Anjlok (<80K) / Resesi Ketakutan",
                        condition="Pengangguran melonjak >4.4%",
                        ihsg_impact="IHSG Turun Bersama Wall Street akibat Risk-Off Global.",
                        sector_impact="Komoditas Siklikal dan Energi tertekan tajam.",
                        favored_stocks=["Defensif Teleko & Emas (TLKM, ANTM)"],
                        pressured_stocks=["ADRO", "MEDC", "UNTR", "GOTO"]
                    )
                ],
                "actionable_strategy": "Hindari saham komoditas dengan leverage tinggi saat malam rilis NFP jika volatilitas pasar valuta bergejolak.",
                "is_tentative": False
            },

            # 6. OPEC+ Ministerial Meeting (Crude Oil Production Quota)
            {
                "id": "opec-plus-meeting",
                "title": "Pertemuan Tingkat Menteri OPEC+ (Keputusan Kuota Produksi Minyak Mentah)",
                "country": "Global / OPEC",
                "country_code": "GLOBAL",
                "flag_emoji": "🌐",
                "institution": "OPEC & Sekutu (OPEC+)",
                "category": EventCategory.COMMODITY_ENERGY,
                "category_label": "Komoditas & Energi",
                "event_date": d_p14,
                "time_utc7": "17:00 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "Perpanjang Pemangkasan 2.2M bpd",
                "forecast_val": "Perpanjang Sukarela hingga Q4",
                "actual_val": None,
                "unit": "Bbl/Day",
                "summary": "Keputusan kartel produsen minyak OPEC+ (termasuk Arab Saudi dan Rusia) mengenai kuota produksi minyak mentah. Pemangkasan suplai mendongkrak harga minyak Brent/WTI, menguntungkan emiten migas dan distribusi BBM.",
                "transmission_mechanism": "Kenaikan harga minyak mentah global langsung meningkatkan Average Selling Price (ASP) dan pendapatan lifting migas MEDC dan ENRG. Di sisi lain, kenaikan harga minyak yang terlalu tinggi membebani biaya bahan bakar dan subsidi energi pemerintah.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="MEDC",
                        name="Medco Energi Internasional Tbk",
                        sector="Energy / Migas",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Laba bersih sangat sensitif terhadap setiap kenaikan $1/barel harga minyak Brent."
                    ),
                    ImpactedStockItem(
                        ticker="AKRA",
                        name="AKR Corporindo Tbk",
                        sector="Energy / Distribusi BBM & Logistik",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Formula margin distribusi BBM industri berbasis formula harga MOPS / Brent."
                    ),
                    ImpactedStockItem(
                        ticker="PGAS",
                        name="Perusahaan Gas Negara Tbk",
                        sector="Utilities / Distribusi Gas Bumi",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Harga substitusi energi gas bumi menjadi lebih kompetitif dibanding minyak solar industri."
                    ),
                    ImpactedStockItem(
                        ticker="ICBP",
                        name="Indofood CBP Sukses Makmur Tbk",
                        sector="Consumer Goods",
                        sensitivity="RINGAN",
                        expected_bias=MarketBias.BEARISH,
                        impact_reason="Kenaikan harga minyak menaikkan biaya kemasan plastik (resin/petrokimia) dan ongkos logistik."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="OPEC+ Perpanjang Pemangkasan Produksi Minyak",
                        condition="Minyak Brent melonjak ke $85-$90/bbl",
                        ihsg_impact="Sektor Energi menguat tajam, IHSG ditopang saham-saham tambang migas.",
                        sector_impact="Oil & Gas, Coal, dan Shipping menguat.",
                        favored_stocks=["MEDC", "AKRA", "PGAS"],
                        pressured_stocks=["Sektor Penerbangan & Logistik Bahan Bakar"]
                    ),
                    ScenarioItem(
                        scenario_name="OPEC+ Longgarkan Kuota / Tambah Pasokan Minyak",
                        condition="Minyak Brent anjlok ke <$70/bbl",
                        ihsg_impact="Sektor Energi terkoreksi, namun emiten konsumer dan manufaktur diuntungkan penurunan biaya energi.",
                        sector_impact="Consumer Goods dan Kimia/Petrokimia membaik.",
                        favored_stocks=["ICBP", "INDF", "KLBF"],
                        pressured_stocks=["MEDC", "AKRA"]
                    )
                ],
                "actionable_strategy": "Buy on momentum pada MEDC dan AKRA bila pernyataan resmi OPEC+ mengonfirmasi komitmen pengetatan suplai.",
                "is_tentative": False
            },

            # 7. China Caixin Manufacturing PMI & Economic Data
            {
                "id": "china-caixin-pmi",
                "title": "Rilis Data PMI Manufaktur China & Stimulus Ekonomi PBOC",
                "country": "China",
                "country_code": "CN",
                "flag_emoji": "🇨🇳",
                "institution": "Caixin / S&P Global China & PBOC",
                "category": EventCategory.COMMODITY_ENERGY,
                "category_label": "Komoditas & Permintaan Ekspor",
                "event_date": d_p18,
                "time_utc7": "08:45 WIB",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "49.8",
                "forecast_val": "50.4",
                "actual_val": None,
                "unit": "Index Point",
                "summary": "China adalah mitra dagang terbesar Indonesia dan konsumen utama komoditas batu bara, nikel, tembaga, dan kelapa sawit (CPO). Ekspansi PMI Manufaktur China (>50.0) menjadi pemicu kenaikan harga komoditas tambang IDX.",
                "transmission_mechanism": "Aktivitas pabrik dan sektor properti China yang membaik meningkatkan permintaan impor batu bara termal & metalurgi dari ADRO, PTBA, ITMG, ADMR serta nikel dari ANTM dan INCO. Kebijakan stimulus moneter dari People's Bank of China (PBOC) memberikan dorongan likuiditas komoditas global.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="ADRO",
                        name="Adaro Energy Indonesia Tbk",
                        sector="Energy / Batu Bara",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="China adalah salah satu negara tujuan ekspor utama batu bara termal Adaro."
                    ),
                    ImpactedStockItem(
                        ticker="ADMR",
                        name="Adaro Minerals Indonesia Tbk",
                        sector="Basic Materials / Coking Coal",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Batu bara metalurgi (coking coal) adalah bahan baku krusial bagi pabrik peleburan baja di China."
                    ),
                    ImpactedStockItem(
                        ticker="PTBA",
                        name="Bukit Asam Tbk",
                        sector="Energy / Batu Bara",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kenaikan indeks harga batu bara Newcastle/ICI mengangkat harga jual rata-rata."
                    ),
                    ImpactedStockItem(
                        ticker="ANTM",
                        name="Aneka Tambang Tbk",
                        sector="Basic Materials / Nikel & Emas",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Permintaan bijih nikel dan feronikel terkait langsung dengan utilisasi smelter dan rantai pasok baterai EV di China."
                    ),
                    ImpactedStockItem(
                        ticker="UNTR",
                        name="United Tractors Tbk",
                        sector="Industrials / Alat Berat",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Penjualan alat berat Komatsu dan volume kontraktor penambangan Pama meningkat bila tambang batu bara aktif berproduksi."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="PMI Manufaktur China Ekspansif (>51.0)",
                        condition="Aktual > 51.0 + Stimulus PBOC Agresif",
                        ihsg_impact="Rally Saham Tambang dan Material Dasar, IHSG terangkat.",
                        sector_impact="Energy (Batu Bara), Logam (Nikel/Tembaga/Emas), dan Alat Berat melesat.",
                        favored_stocks=["ADMR", "ADRO", "PTBA", "ANTM", "UNTR"],
                        pressured_stocks=[]
                    ),
                    ScenarioItem(
                        scenario_name="PMI Manufaktur China Terkontraksi (<49.0)",
                        condition="Aktual < 49.0 (Pelemahan Properti China)",
                        ihsg_impact="Koreksi pada saham-saham komoditas ekspor.",
                        sector_impact="Tekanan pada harga batu bara dan nikel dunia.",
                        favored_stocks=["Defensif Konsumer Domestik (ICBP, MYOR)"],
                        pressured_stocks=["ADRO", "ADMR", "PTBA", "ANTM"]
                    )
                ],
                "actionable_strategy": "Fokus pada emiten batubara metalurgi bernilai tambah tinggi seperti ADMR serta emiten dengan kas bersih melimpah saat data China mulai menunjukkan tanda-tanda 'bottoming out'.",
                "is_tentative": False
            },

            # 8. Indonesia Trade Balance & Foreign Exchange Reserves
            {
                "id": "id-trade-balance",
                "title": "Rilis Neraca Perdagangan & Cadangan Devisa RI",
                "country": "Indonesia",
                "country_code": "ID",
                "flag_emoji": "🇮🇩",
                "institution": "Badan Pusat Statistik & Bank Indonesia",
                "category": EventCategory.TRADE_MACRO,
                "category_label": "Neraca & Devisa",
                "event_date": d_p7,
                "time_utc7": "11:00 WIB",
                "impact_level": ImpactLevel.MEDIUM,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "Surplus $2.39 B",
                "forecast_val": "Surplus $2.15 B",
                "actual_val": None,
                "unit": "USD Billion",
                "summary": "Neraca perdagangan Indonesia mencatatkan rekor surplus beruntun selama puluhan bulan. Angka surplus yang solid menopang posisi cadangan devisa (cadev) Bank Indonesia dan menjadi bantalan utama stabilitas nilai tukar Rupiah dari guncangan eksternal.",
                "transmission_mechanism": "Surplus perdagangan yang konsisten meyakinkan investor asing bahwa defisit transaksi berjalan (CAD) Indonesia terkendali di bawah 1.5% PDB, menaikkan kepercayaan terhadap aset pasar modal berbasis Rupiah.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Stabilitas nilai tukar Rupiah menjaga kestabilan sistem perbankan nasional."
                    ),
                    ImpactedStockItem(
                        ticker="ASII",
                        name="Astra International Tbk",
                        sector="Consumer Discretionary",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Komponen impor otomotif (CKD/CBU) stabil dengan fluktuasi valas yang terjaga."
                    ),
                    ImpactedStockItem(
                        ticker="ADRO",
                        name="Adaro Energy Indonesia Tbk",
                        sector="Energy / Komoditas",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kontributor utama penerimaan devisa ekspor nasional non-migas."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Surplus Neraca Dagang Diatas Ekspektasi (>$2.5 Miliar)",
                        condition="Ekspor CPO & Nikel Solid",
                        ihsg_impact="Sentimen Positif untuk Nilai Tukar Rupiah dan Obligasi SUN.",
                        sector_impact="Perbankan dan Manufaktur bergerak naik.",
                        favored_stocks=["BBCA", "BMRI", "ASII", "ICBP"],
                        pressured_stocks=[]
                    )
                ],
                "actionable_strategy": "Surplus yang berlanjut mengindikasikan momentum makro fundamental Indonesia yang kokoh untuk investasi jangka menengah-panjang.",
                "is_tentative": False
            },

            # 9. MSCI Index Rebalancing (Quarterly / Semi-Annual Review)
            {
                "id": "msci-index-rebalance",
                "title": "Efektif Rebalancing Indeks Global MSCI (MSCI Indonesia Index)",
                "country": "Global / IDX",
                "country_code": "GLOBAL",
                "flag_emoji": "⚖️",
                "institution": "Morgan Stanley Capital International (MSCI)",
                "category": EventCategory.INDEX_REBALANCE,
                "category_label": "Rebalancing Indeks Global",
                "event_date": d_p22,
                "time_utc7": "15:50 WIB (Closing Session)",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "Inflow Rebalancing Mei",
                "forecast_val": "Potensi Inflow Ticker Baru",
                "actual_val": None,
                "unit": "Net Foreign Flow",
                "summary": "Perombakan konstituen dan bobot (weighting) indeks global MSCI Standard Cap & Small Cap. Dana kelolaan pasif global (ETF & Mutual Funds pelacak MSCI) wajib mengeksekusi pembelian/penjualan pada sesi closing auction (15:50 - 16:00 WIB), menciptakan lonjakan volume transaksi masif triliunan rupiah.",
                "transmission_mechanism": "Saham yang masuk (inclusion) ke MSCI Global Standard Index mendapatkan arus beli dana pasif otomatis bernilai ratusan juta dolar AS. Sebaliknya, saham yang diturunkan bobotnya atau didepak (exclusion) akan menghadapi tekanan jual teknikal pada tanggal efektif.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Saham dengan bobot terbesar di MSCI Indonesia; volume transaksi pre-closing melonjak tajam."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Saham pilar utama indeks MSCI Emerging Markets dengan turnover raksasa."
                    ),
                    ImpactedStockItem(
                        ticker="TLKM",
                        name="Telkom Indonesia (Persero) Tbk",
                        sector="Telecommunication",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Penyesuaian bobot sektor infrastruktur telekomunikasi."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Net Foreign Inflow Masif pada Sesi Pre-Closing",
                        condition="Volume IHSG melonjak >Rp 20 Triliun dalam 10 menit terakhir",
                        ihsg_impact="Lonjakan Volatilitas Harga di Jam 15.50 - 16.00 WIB.",
                        sector_impact="Saham konstituen MSCI mengalami lonjakan transaksi super likuid.",
                        favored_stocks=["Saham yang ditambahkan ke indeks (Inclusion candidates)"],
                        pressured_stocks=["Saham yang dikeluarkan dari indeks (Deletion candidates)"]
                    )
                ],
                "actionable_strategy": "Bagi swing trader, manfaatkan potensi 'MSCI Inclusion Momentum' 2-3 minggu sebelum tanggal efektif, lalu take profit bertahap pada hari efektif saat dana pasif mengeksekusi pembelian.",
                "is_tentative": False
            },

            # 10. Indonesian Corporate Dividend Cum-Date Season
            {
                "id": "idx-dividend-cum-date-season",
                "title": "Musim Cum-Date Dividen Emiten Big Caps & High Yielders IDX",
                "country": "Indonesia",
                "country_code": "ID",
                "flag_emoji": "💰",
                "institution": "Bursa Efek Indonesia (IDX) / KSEI",
                "category": EventCategory.DIVIDEND,
                "category_label": "Kalender Dividen & Yield",
                "event_date": d_p28,
                "time_utc7": "16:00 WIB (Pasar Reguler)",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "Yield Rata-rata 7.5%",
                "forecast_val": "Yield Potensial 8-12%",
                "actual_val": None,
                "unit": "Dividend Yield",
                "summary": "Tanggal Cum-Date adalah hari terakhir investor berhak mencatatkan diri untuk menerima dividen tunai emiten di pasar reguler. Saham-saham dengan dividend yield jumbo (seperti emiten batu bara dan perbankan BUMN) seringkali mengalami 'Dividend Rally' menjelang cum-date dan 'Dividend Trap' pada saat Ex-Date.",
                "transmission_mechanism": "Permintaan beli meningkat tajam beberapa pekan menjelang cum-date dari para pemburu dividen (dividend hunters). Pada hari Ex-Date (H+1 Cum-Date), harga saham biasanya terkoreksi sebesar nilai dividen per saham yang dibagikan.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="PTBA",
                        name="Bukit Asam Tbk",
                        sector="Energy / Batu Bara",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Historis Dividend Payout Ratio mendekati 100% dengan potensi dividend yield 10% - 14%."
                    ),
                    ImpactedStockItem(
                        ticker="ADRO",
                        name="Adaro Energy Indonesia Tbk",
                        sector="Energy / Batu Bara",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Komitmen pembagian dividen final dan dividen spesial yang sangat royal bagi pemegang saham."
                    ),
                    ImpactedStockItem(
                        ticker="BBRI",
                        name="Bank Rakyat Indonesia (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Payout ratio konsisten >70% memberikan dividend yield 5% - 7% yang menarik bagi investor institusi."
                    ),
                    ImpactedStockItem(
                        ticker="UNTR",
                        name="United Tractors Tbk",
                        sector="Industrials",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Arus kas operasi yang sangat sehat menjamin dividen jumbo tahunan."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Dividend Payout Ratio >80% (Diatas Konsensus)",
                        condition="RUPS menyetujui dividen jumbo",
                        ihsg_impact="Penguatan harga saham cum-date rally berlanjut.",
                        sector_impact="Emiten BUMN Tambang & Perbankan menjadi primadona.",
                        favored_stocks=["PTBA", "ADRO", "UNTR", "BBRI", "BMRI"],
                        pressured_stocks=[]
                    ),
                    ScenarioItem(
                        scenario_name="Penurunan Dividen Akibat Kebutuhan Capex Ekspansi",
                        condition="Payout ratio diturunkan <40%",
                        ihsg_impact="Kekecewaan pasar jangka pendek, koreksi pada saham terkait.",
                        sector_impact="Saham dividend play terkoreksi.",
                        favored_stocks=[],
                        pressured_stocks=["PTBA", "ADRO"]
                    )
                ],
                "actionable_strategy": "Hindari membeli tepat di hari Cum-Date karena risiko Dividend Trap di hari Ex-Date; strategi terbaik adalah akumulasi 1-2 bulan sebelum RUPS dan lakukan taking profit sebagian saat cum-date rally.",
                "is_tentative": False
            },

            # 11. IDX Earnings Season (Rilis Lapkeu Kuartalan / Tahunan)
            {
                "id": "idx-earnings-season",
                "title": "Musim Rilis Laporan Keuangan Emiten IDX (Earnings Season Q3 / FY)",
                "country": "Indonesia",
                "country_code": "ID",
                "flag_emoji": "🏢",
                "institution": "Bursa Efek Indonesia & Emiten",
                "category": EventCategory.CORPORATE_ACTION,
                "category_label": "Laporan Keuangan & RUPS",
                "event_date": d_p35,
                "time_utc7": "Bursa Efek Indonesia",
                "impact_level": ImpactLevel.HIGH,
                "market_scope": MarketScope.INDONESIA,
                "previous_val": "Pertumbuhan Laba +8.2% YoY",
                "forecast_val": "Pertumbuhan Laba +9.5% YoY",
                "actual_val": None,
                "unit": "EPS Growth",
                "summary": "Periode pelaporan kinerja keuangan kuartalan dan tahunan emiten tercatat di BEI. Pertumbuhan laba bersih (Net Profit) dan margin operasional di atas ekspektasi konsensus analis memicu kenaikan target harga (re-rating valuation) oleh sekuritas domestik dan asing.",
                "transmission_mechanism": "Emiten yang mencetak 'Earnings Beat' (laba melampaui konsensus) mendapatkan upgrade rekomendasi dan target price, mendorong apresiasi harga saham. Sebaliknya emiten dengan 'Earnings Miss' atau lonjakan NPL/beban bunga akan mengalami downgrade valuasi.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="BBCA",
                        name="Bank Central Asia Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kualitas kredit (LAR & NPL) terjaga di level terendah industri dengan profitabilitas rekor baru."
                    ),
                    ImpactedStockItem(
                        ticker="BMRI",
                        name="Bank Mandiri (Persero) Tbk",
                        sector="Financials (Perbankan)",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Efisiensi digital via Livin' & Kopra terus menekan Cost to Income Ratio (CIR)."
                    ),
                    ImpactedStockItem(
                        ticker="ICBP",
                        name="Indofood CBP Sukses Makmur Tbk",
                        sector="Consumer Staples",
                        sensitivity="TINGGI",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kinerja penjualan internasional Pinehill dan margin segmen mi instan menjadi sorotan utama."
                    ),
                    ImpactedStockItem(
                        ticker="TLKM",
                        name="Telkom Indonesia (Persero) Tbk",
                        sector="Telecommunication",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.NEUTRAL_VOLATILE,
                        impact_reason="Monetisasi data center (NeutraDC) dan integrasi fixed-mobile convergence (FMC) IndiHome."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Mayoritas Big Caps Cetak Double-Digit Profit Growth",
                        condition="Pertumbuhan Laba Bersih >10% YoY",
                        ihsg_impact="IHSG Tembus All-Time High baru, target valuasi PER IHSG naik.",
                        sector_impact="Big Banks dan Consumer Staples memimpin kenaikan.",
                        favored_stocks=["BBCA", "BMRI", "ICBP", "KLBF"],
                        pressured_stocks=[]
                    )
                ],
                "actionable_strategy": "Gunakan KeyStats Scoring Engine untuk menyaring emiten dengan skor kualitas (Piotroski F-Score > 7) dan pertumbuhan pendapatan stabil sebelum tanggal rilis lapkeu.",
                "is_tentative": False
            },

            # 12. US GDP Growth Rate (Gross Domestic Product)
            {
                "id": "us-gdp-growth-rate",
                "title": "Rilis Data Pertumbuhan Ekonomi AS (US GDP Annualized QoQ)",
                "country": "Amerika Serikat",
                "country_code": "US",
                "flag_emoji": "🇺🇸",
                "institution": "US Bureau of Economic Analysis (BEA)",
                "category": EventCategory.INFLATION_GDP,
                "category_label": "Inflasi & Pertumbuhan Ekonomi",
                "event_date": d_p14,
                "time_utc7": "19:30 WIB",
                "impact_level": ImpactLevel.MEDIUM,
                "market_scope": MarketScope.US_GLOBAL,
                "previous_val": "2.8%",
                "forecast_val": "2.9%",
                "actual_val": None,
                "unit": "% QoQ Ann.",
                "summary": "Pertumbuhan PDB AS mencerminkan kekuatan belanja konsumen dan investasi korporasi di negara ekonomi terbesar dunia. Pertumbuhan ekonomi AS yang resilien tanpa lonjakan inflasi mengonfirmasi skenario 'Soft Landing' yang mendukung stabilitas bursa saham global.",
                "transmission_mechanism": "Pertumbuhan ekonomi AS yang solid menjamin kelangsungan volume perdagangan ekspor dunia dan konsumsi energi, menopang harga komoditas ekspor Indonesia.",
                "impacted_stocks": [
                    ImpactedStockItem(
                        ticker="ADRO",
                        name="Adaro Energy Indonesia Tbk",
                        sector="Energy",
                        sensitivity="SEDANG",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Sentimen permintaan energi global tetap terjaga kuat."
                    ),
                    ImpactedStockItem(
                        ticker="ASII",
                        name="Astra International Tbk",
                        sector="Consumer Discretionary",
                        sensitivity="RINGAN",
                        expected_bias=MarketBias.BULLISH,
                        impact_reason="Kondisi ekonomi makro global yang kondusif menjaga stabilitas pasar keuangan domestik."
                    )
                ],
                "scenarios": [
                    ScenarioItem(
                        scenario_name="Pertumbuhan PDB AS Solid (2.5% - 3.0%)",
                        condition="Sesuai ekspektasi Soft Landing",
                        ihsg_impact="IHSG Kondusif, sentimen bullish pasar saham global.",
                        sector_impact="Ekuitas global menguat.",
                        favored_stocks=["BBCA", "BMRI", "ADRO", "MEDC"],
                        pressured_stocks=[]
                    )
                ],
                "actionable_strategy": "Pertahankan alokasi saham berbobot besar pada portofolio saat data PDB AS mengonfirmasi terhindarnya resesi global.",
                "is_tentative": False
            }
        ]

    def _compute_status_and_countdown(self, event_date_str: str, reference_date: Optional[date] = None) -> (int, str, str):
        """
        Computes days_until, relative_time_label, and status code.
        """
        ref = reference_date or date.today()
        try:
            ev_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
        except Exception:
            return 0, "Tentatif", "UPCOMING"

        delta = (ev_date - ref).days

        if delta < 0:
            days_ago = abs(delta)
            label = f"Selesai ({days_ago} hari lalu)" if days_ago > 1 else "Selesai (Kemarin)"
            status = "COMPLETED"
        elif delta == 0:
            label = "Hari Ini 🚨"
            status = "TODAY"
        elif delta == 1:
            label = "Besok"
            status = "UPCOMING"
        elif delta <= 7:
            label = f"Dalam {delta} Hari"
            status = "UPCOMING"
        elif delta <= 30:
            weeks = max(1, round(delta / 7))
            label = f"Dalam {delta} Hari (~{weeks} Minggu)"
            status = "UPCOMING"
        else:
            label = f"Dalam {delta} Hari"
            status = "UPCOMING"

        return delta, label, status

    def get_calendar_agendas(
        self,
        scope: Optional[str] = None,
        category: Optional[str] = None,
        impact_level: Optional[str] = None,
        timeframe: Optional[str] = None,
        search: Optional[str] = None,
        ticker: Optional[str] = None,
        reference_date: Optional[date] = None
    ) -> CalendarResponse:
        """
        Returns full calendar payload with filtered items, stats, upcoming highlights, and sector sensitivity overview.
        """
        raw_items = self._get_base_dataset(reference_date)
        agendas: List[CalendarAgendaItem] = []

        all_affected_tickers = set()

        for r in raw_items:
            days_until, rel_label, status = self._compute_status_and_countdown(r["event_date"], reference_date)
            
            agenda = CalendarAgendaItem(
                id=r["id"],
                title=r["title"],
                country=r["country"],
                country_code=r["country_code"],
                flag_emoji=r["flag_emoji"],
                institution=r["institution"],
                category=r["category"],
                category_label=r["category_label"],
                event_date=r["event_date"],
                time_utc7=r["time_utc7"],
                days_until=days_until,
                relative_time_label=rel_label,
                status=status,
                impact_level=r["impact_level"],
                market_scope=r["market_scope"],
                previous_val=r.get("previous_val"),
                forecast_val=r.get("forecast_val"),
                actual_val=r.get("actual_val"),
                unit=r.get("unit"),
                summary=r["summary"],
                transmission_mechanism=r["transmission_mechanism"],
                impacted_stocks=r["impacted_stocks"],
                scenarios=r["scenarios"],
                actionable_strategy=r["actionable_strategy"],
                is_tentative=r.get("is_tentative", False)
            )

            for st in agenda.impacted_stocks:
                all_affected_tickers.add(st.ticker.upper())

            # Apply filters
            if scope and scope.upper() != "ALL":
                if agenda.market_scope.value != scope.upper():
                    continue

            if category and category.upper() != "ALL":
                if agenda.category.value != category.upper():
                    continue

            if impact_level and impact_level.upper() != "ALL":
                if agenda.impact_level.value != impact_level.upper():
                    continue

            if timeframe and timeframe.upper() != "ALL":
                tf = timeframe.upper()
                if tf == "TODAY" and agenda.days_until != 0:
                    continue
                elif tf == "THIS_WEEK" and not (0 <= agenda.days_until <= 7):
                    continue
                elif tf == "THIS_MONTH" and not (0 <= agenda.days_until <= 31):
                    continue
                elif tf == "UPCOMING" and agenda.days_until < 0:
                    continue

            if ticker:
                clean_t = ticker.upper().replace(".JK", "").strip()
                matches_ticker = any(s.ticker.upper() == clean_t for s in agenda.impacted_stocks)
                if not matches_ticker:
                    continue

            if search:
                q = search.lower().strip()
                matches_title = q in agenda.title.lower()
                matches_country = q in agenda.country.lower() or q in agenda.country_code.lower()
                matches_inst = q in agenda.institution.lower()
                matches_summary = q in agenda.summary.lower()
                matches_cat = q in agenda.category_label.lower()
                matches_stock = any(
                    q in s.ticker.lower() or q in s.name.lower() or q in s.sector.lower()
                    for s in agenda.impacted_stocks
                )
                if not (matches_title or matches_country or matches_inst or matches_summary or matches_cat or matches_stock):
                    continue

            agendas.append(agenda)

        # Sort agendas: upcoming closest first (0, 1, 2, ...), then past items at the bottom
        def sort_key(item: CalendarAgendaItem):
            # If >= 0: sort ascending from 0 to +inf
            # If < 0: place after all upcoming, sorted most recent first (-1 before -10)
            if item.days_until >= 0:
                return (0, item.days_until)
            else:
                return (1, -item.days_until)

        agendas.sort(key=sort_key)

        # 2. Compute Global Stats
        all_raw = self._get_base_dataset(reference_date)
        high_impact_cnt = sum(1 for r in all_raw if r["impact_level"] == ImpactLevel.HIGH)
        dom_cnt = sum(1 for r in all_raw if r["market_scope"] == MarketScope.INDONESIA)
        us_cnt = sum(1 for r in all_raw if r["market_scope"] == MarketScope.US_GLOBAL)

        stats = CalendarStats(
            total_events=len(all_raw),
            high_impact_count=high_impact_cnt,
            domestic_count=dom_cnt,
            us_global_count=us_cnt,
            total_affected_stocks=len(all_affected_tickers)
        )

        # 3. Top 3 Upcoming Highlights (High Impact & Upcoming closest)
        upcoming_items = [a for a in agendas if a.days_until >= 0]
        high_upcoming = [a for a in upcoming_items if a.impact_level == ImpactLevel.HIGH]
        upcoming_highlights = high_upcoming[:3] if len(high_upcoming) >= 3 else upcoming_items[:3]

        # 4. Sector Sensitivities
        sector_sensitivities = self.get_sector_sensitivities()

        return CalendarResponse(
            stats=stats,
            agendas=agendas,
            upcoming_highlights=upcoming_highlights,
            sector_sensitivities=sector_sensitivities,
            generated_at_desc=datetime.now().strftime("%d %B %Y, %H:%M WIB")
        )

    def get_agenda_by_id(self, agenda_id: str, reference_date: Optional[date] = None) -> Optional[CalendarAgendaItem]:
        resp = self.get_calendar_agendas(reference_date=reference_date)
        for a in resp.agendas:
            if a.id == agenda_id:
                return a
        return None

    def get_sector_sensitivities(self) -> List[SectorSensitivityItem]:
        """
        Returns structured sensitivity matrix of IDX sectors against key macro catalysts.
        """
        return [
            SectorSensitivityItem(
                sector_name="Perbankan & Keuangan (Financials)",
                icon="🏦",
                primary_catalysts=["BI-Rate", "Fed Funds Rate", "Foreign Capital Inflow", "NPL / Kualitas Kredit"],
                key_tickers=["BBCA", "BBRI", "BMRI", "BBNI", "BBTN", "BDMN"],
                sensitivity_level="Sangat Tinggi",
                macro_exposure="Sensitif terhadap selisih suku bunga (NIM), likuiditas moneter perbankan, dan arus dana investor institusi asing."
            ),
            SectorSensitivityItem(
                sector_name="Properti & Real Estate",
                icon="🏢",
                primary_catalysts=["Suku Bunga KPR / BI-Rate", "PPN DTP Properti", "Inflasi Bahan Bangunan"],
                key_tickers=["BSDE", "CTRA", "PWON", "SMRA", "ASRI"],
                sensitivity_level="Sangat Tinggi",
                macro_exposure="Tingkat suku bunga KPR berbanding terbalik dengan angka pra-penjualan (marketing sales) properti residensial."
            ),
            SectorSensitivityItem(
                sector_name="Pertambangan & Energi (Mining & Oil/Gas)",
                icon="⛏️",
                primary_catalysts=["PMI Manufaktur China", "Keputusan OPEC+", "Kurs USD/IDR", "Harga Komoditas Acuan (ICI/Brent)"],
                key_tickers=["ADRO", "PTBA", "ITMG", "ADMR", "MEDC", "AKRA", "ANTM", "INCO"],
                sensitivity_level="Sangat Tinggi",
                macro_exposure="Pendapatan berbasis USD dengan harga komoditas global; diuntungkan oleh penguatan Dolar dan ekspansi industri China."
            ),
            SectorSensitivityItem(
                sector_name="Konsumer Primer (Consumer Staples)",
                icon="🛒",
                primary_catalysts=["Inflasi Pangan BPS", "Daya Beli / UMR", "Kurs Rupiah (Bahan Baku Impor)"],
                key_tickers=["ICBP", "INDF", "MYOR", "UNVR", "AMRT", "CMRY"],
                sensitivity_level="Tinggi",
                macro_exposure="Pelemahan Rupiah menekan margin kotor bahan baku impor (gandum/kedelai); sebaliknya inflasi rendah menjaga volume konsumsi."
            ),
            SectorSensitivityItem(
                sector_name="Teknologi & Growth Stocks",
                icon="🚀",
                primary_catalysts=["Global Yield US 10Y", "Fed Policy Stance", "Risk Appetite Modal Ventura"],
                key_tickers=["GOTO", "BUKA", "EMTK", "DCII"],
                sensitivity_level="Sangat Tinggi",
                macro_exposure="Valuasi DCF berbasis discount rate global; sangat diuntungkan oleh tren pemangkasan suku bunga global."
            ),
            SectorSensitivityItem(
                sector_name="Otomotif & Multifinance",
                icon="🚗",
                primary_catalysts=["Suku Bunga Kredit Multifinance", "Insentif Pajak EV", "Daya Beli Konsumen"],
                key_tickers=["ASII", "AUTO", "DRMA"],
                sensitivity_level="Sedang",
                macro_exposure="Sebagian besar pembelian mobil & motor menggunakan kredit pembiayaan yang sensitif terhadap BI-Rate."
            ),
            SectorSensitivityItem(
                sector_name="Telekomunikasi & Menara",
                icon="📡",
                primary_catalysts=["Tingkat Suku Bunga (Beban Utang Capex)", "Daya Beli Paket Data", "Monetisasi Data Center"],
                key_tickers=["TLKM", "ISAT", "EXCL", "TOWR", "TBIG"],
                sensitivity_level="Sedang",
                macro_exposure="Sektor defensif dengan arus kas stabil, namun emiten menara sensitif terhadap biaya bunga pembiayaan ekspansi."
            )
        ]
