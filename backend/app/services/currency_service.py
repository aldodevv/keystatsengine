"""
Currency Service for Real-time USD/IDR Exchange Rates and Currency Conversion.
Provides multi-source failover (Yahoo Finance, Open Exchange Rates, Frankfurter API)
with in-memory caching and resilient fallback.
"""

import time
import datetime
from typing import Optional, Tuple
import requests
from app.models.currency import CurrencyRateResponse, CurrencyConversionResponse


class CurrencyService:
    _cached_rate_data: Optional[CurrencyRateResponse] = None
    _cache_timestamp: float = 0
    _CACHE_TTL_SECONDS: float = 300.0  # 5 minutes cache TTL
    _FALLBACK_USD_IDR: float = 17712.0

    def __init__(self, cache_ttl_seconds: float = 300.0):
        self.cache_ttl_seconds = cache_ttl_seconds

    def get_live_rate(self, force_refresh: bool = False) -> CurrencyRateResponse:
        """
        Fetches the current live USD/IDR exchange rate.
        Uses in-memory cache if within TTL, unless force_refresh is True.
        """
        now = time.time()
        if not force_refresh and self._cached_rate_data and (now - self._cache_timestamp < self.cache_ttl_seconds):
            return self._cached_rate_data

        # Attempt fetching from multiple providers in order of preference
        rate, prev_close, source = self._fetch_rate_multi_source()

        if not rate or rate <= 0:
            if self._cached_rate_data:
                return self._cached_rate_data
            rate = self._FALLBACK_USD_IDR
            prev_close = self._FALLBACK_USD_IDR
            source = "Default Fallback (Cached)"

        idr_to_usd = 1.0 / rate if rate > 0 else 0.0

        change_24h = round(rate - prev_close, 2) if prev_close else 0.0
        change_pct_24h = round((change_24h / prev_close) * 100, 2) if prev_close and prev_close > 0 else 0.0

        dt_now = datetime.datetime.now()
        iso_time = dt_now.isoformat()
        formatted_time = dt_now.strftime("%d %b %Y, %H:%M WIB")

        rate_resp = CurrencyRateResponse(
            base_currency="USD",
            target_currency="IDR",
            usd_to_idr=round(rate, 2),
            idr_to_usd=round(idr_to_usd, 8),
            previous_close=round(prev_close, 2) if prev_close else None,
            change_24h=change_24h,
            change_pct_24h=change_pct_24h,
            last_updated=iso_time,
            last_updated_formatted=formatted_time,
            source=source,
            formatted_rate=f"1 USD = Rp {rate:,.0f}"
        )

        CurrencyService._cached_rate_data = rate_resp
        CurrencyService._cache_timestamp = now
        return rate_resp

    def _fetch_rate_multi_source(self) -> Tuple[Optional[float], Optional[float], str]:
        """
        Attempts to fetch live exchange rate from available sources.
        Returns (rate, prev_close, source_name).
        """
        # 1. Primary: Yahoo Finance fast_info quote for USDIDR=X
        try:
            import yfinance as yf
            ticker = yf.Ticker("USDIDR=X")
            fast_info = getattr(ticker, "fast_info", None)
            if fast_info:
                last_price = getattr(fast_info, "last_price", None)
                prev_close = getattr(fast_info, "previous_close", None)
                if last_price and last_price > 5000:
                    return float(last_price), float(prev_close) if prev_close else float(last_price), "Yahoo Finance (Real-time FX)"
        except Exception:
            pass

        # 2. Secondary: Open Exchange Rates API (open.er-api.com)
        try:
            resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                rate = data.get("rates", {}).get("IDR")
                if rate and rate > 5000:
                    return float(rate), float(rate), "Open Exchange Rates API"
        except Exception:
            pass

        # 3. Tertiary: Frankfurter Central Bank API
        try:
            resp = requests.get("https://api.frankfurter.app/latest?from=USD&to=IDR", timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                rate = data.get("rates", {}).get("IDR")
                if rate and rate > 5000:
                    return float(rate), float(rate), "Frankfurter Central Bank FX"
        except Exception:
            pass

        return None, None, "Unavailable"

    def convert(self, amount: float, from_currency: str = "IDR", to_currency: str = "USD") -> CurrencyConversionResponse:
        """
        Converts an amount from one currency to another using the latest live exchange rate.
        """
        from_curr = from_currency.upper().strip()
        to_curr = to_currency.upper().strip()
        live_rate = self.get_live_rate()

        usd_to_idr = live_rate.usd_to_idr
        idr_to_usd = live_rate.idr_to_usd

        if from_curr == to_curr:
            converted = amount
            rate_used = 1.0
            fmt_orig = self.format_amount(amount, from_curr)
            fmt_conv = self.format_amount(converted, to_curr)
        elif from_curr == "IDR" and to_curr == "USD":
            converted = amount * idr_to_usd
            rate_used = idr_to_usd
            fmt_orig = f"Rp {amount:,.0f}"
            fmt_conv = f"${converted:,.2f}"
        elif from_curr == "USD" and to_curr == "IDR":
            converted = amount * usd_to_idr
            rate_used = usd_to_idr
            fmt_orig = f"${amount:,.2f}"
            fmt_conv = f"Rp {converted:,.0f}"
        else:
            # Default to IDR -> USD
            converted = amount * idr_to_usd
            rate_used = idr_to_usd
            fmt_orig = f"{amount:,.2f} {from_curr}"
            fmt_conv = f"{converted:,.2f} {to_curr}"

        return CurrencyConversionResponse(
            amount=amount,
            from_currency=from_curr,
            to_currency=to_curr,
            converted_amount=round(converted, 4),
            rate_used=round(rate_used, 8),
            formatted_original=fmt_orig,
            formatted_converted=fmt_conv,
            last_updated=live_rate.last_updated
        )

    @staticmethod
    def format_amount(amount: float, currency: str) -> str:
        if currency.upper() == "IDR":
            return f"Rp {amount:,.0f}"
        elif currency.upper() == "USD":
            return f"${amount:,.2f}"
        return f"{amount:,.2f} {currency}"
