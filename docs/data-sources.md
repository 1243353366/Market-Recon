# API data sources

This registry distinguishes integrated clients from intended/planned sources. Listing a provider does not mean its data are currently ingested, free, licensed for redistribution, or suitable for investment decisions.

## Implemented public adapters

### SEC EDGAR

The existing starter supports a limited subset of submissions and filing documents. Configure `SEC_USER_AGENT` with an application name and contact address. The collector does not yet provide complete historical pagination or robust filing-specific structured extraction. Official docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces and https://data.sec.gov/.

### FRED

`FredClient` reads series observations and requires a FRED API key. Set `FRED_API_KEY`; register for a key at https://fred.stlouisfed.org/docs/api/api_key.html. Example:

```python
from datetime import date
import os
from market_recon.data_sources_api import FredClient

rows = FredClient(os.environ["FRED_API_KEY"]).observations(
    "CPIAUCSL", start_date=date(2020, 1, 1), end_date=date(2025, 12, 31)
)
```

FRED series can be revised, have different frequencies/units, and publish on different schedules. Keep series metadata and vintage/realtime fields when making time-aware comparisons.

### USAspending.gov

`USASpendingClient` queries the public award search API without credentials. It returns normalized records with award IDs and source URLs. Contract obligations/award ceilings are not necessarily recognized revenue; account for agency, recipient identity, modifications, period of performance, and award type. Official API docs: https://api.usaspending.gov/.

## Provider connectors not implemented

Alpha Vantage, Financial Modeling Prep, ImportYeti, and Quiver are in `market_recon/source_catalog.py` as planned or access-review sources only. Confirm current endpoints, authentication, rate limits, license, permitted caching/redistribution, and free-tier restrictions directly with each provider before implementing. In particular, do not infer an API's existence or free availability from marketing pages, and do not scrape login-gated or paywalled data.

## Common rules

- Keep API keys in environment variables; never commit them.
- Apply explicit timeouts, validate parameters, and surface HTTP errors rather than silently returning fabricated data.
- Preserve source record IDs, original URLs, retrieval timestamps, and raw values.
- Label third-party data separately from official disclosures.
- Avoid using incomplete or delayed sources to imply real-time status.
