# BRIGHTS — Data Sources & Configuration

BRIGHTS (BRI Stock Intelligence) is **real-data-only**. It never fabricates or ships mock
financial data. When no data source is configured or reachable, API endpoints return
`503` with a clear message instead of inventing numbers.

## Configured sources (in priority order)

Priority is controlled by the `DATA_SOURCE_PRIORITY` environment variable
(comma-separated). Default: `sectors,eodhd`.

### 1. Sectors.app (Supertype) — primary, recommended
- Licensed Indonesian financial-data platform. Fundamentals and shareholder/ownership data
  are sourced from **IDX and KSEI** filings, kept current (beyond 2024).
- This is the closest legitimate equivalent to the data brokers rely on.
- Endpoint: `https://api.sectors.app/v2/`
- Auth: header `Authorization: <API_KEY>`
- Configure: `export SECTORS_API_KEY="your_key"`
- Get a key: https://sectors.app

### 2. EODHD — secondary / prices
- Global fundamentals plus realtime quotes and split/dividend-adjusted OHLCV.
- Used for corporate-action-adjusted price charts and as a fundamentals fallback.
- Configure: `export EODHD_API_KEY="your_key"` (the placeholder `demo` is treated as unset)
- Get a key: https://eodhd.com

> **Free-plan limitation:** an EODHD *free* key returns **EOD prices only** — no
> fundamentals and no shareholder data, historical prices limited to ~1 year, and ~20
> requests/day. To use EODHD for fundamentals/ownership you need a paid **Fundamentals**
> plan. Otherwise use Sectors.app as the fundamentals/ownership source.

### KSEI SID statistics (optional enrichment)
- Market-wide Single Investor Identification (SID) counts from KSEI.
- Configure: `export KSEI_STATISTICS_URL="https://your-proxy/ksei-sid.json"`
- Expected JSON: `{"total_sid": 14200000, "equity_sid": 6100000, "as_of_date": "2026-07-31"}`

> **Note:** `https://web.ksei.co.id/publications/Data_Statistik_KSEI` is a **JS-rendered HTML
> page, not a JSON API** — its underlying data endpoints are not publicly addressable, so
> BRIGHTS cannot read it directly. Point `KSEI_STATISTICS_URL` at a JSON endpoint (e.g. an
> internal proxy that mirrors KSEI's published statistics). Until then SID shows as
> "unavailable" rather than being fabricated.

## Example

```bash
export SECTORS_API_KEY="..."       # primary IDX/KSEI-sourced fundamentals & ownership
export EODHD_API_KEY="..."         # prices / adjusted OHLCV
export KSEI_STATISTICS_URL="..."   # optional: retail SID statistics
export DATA_SOURCE_PRIORITY="sectors,eodhd"   # optional: override precedence
```

## Why not scrape idx.co.id directly?

`idx.co.id` is protected by Cloudflare bot management and returns `403` to programmatic
clients. Bypassing that protection (e.g. with a headless browser) violates IDX's Terms of
Service. For a financial application, BRIGHTS uses only **licensed / permitted** sources
(Sectors.app, EODHD, and an operator-provided KSEI feed). The authoritative raw IDX feed
that member brokers use requires a commercial IDX data license.
