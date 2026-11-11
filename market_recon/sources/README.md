# Source adapters

This package defines a shared `NormalizedRecord` schema and a `SourceAdapter` protocol. Adapters return provenance-preserving records; downstream storage, SQL analytics, and RAG indexing should consume the normalized model rather than provider-specific payloads.

## Layout

```text
market_recon/sources/
├── __init__.py
├── schema.py
├── registry.py
├── collections.py
├── sec_edgar.py
├── fred.py
├── usaspending.py
└── quiver.py
```

## Adapter contract

Each adapter exposes `source_id` and `fetch(**kwargs) -> list[NormalizedRecord]`. Records preserve provider IDs, source citation URLs, retrieval timestamps, observed/published dates, entity identifiers, raw provider data, and a license/access status. No adapter should silently substitute sample data or suppress HTTP errors.

## Examples

```python
import os
from datetime import date
from market_recon.data_sources_api import FredClient, USASpendingClient
from market_recon.rag.sec_edgar import SecEdgarClient
from market_recon.sources import SECEdgarAdapter, FREDAdapter, USAspendingAdapter

sec = SECEdgarAdapter(SecEdgarClient(os.environ["SEC_USER_AGENT"]))
filings = sec.fetch(ticker="NVDA", forms={"10-K", "10-Q", "4"}, limit=10)

fred = FREDAdapter(FredClient(os.environ["FRED_API_KEY"]))
macro = fred.fetch(series_id="CPIAUCSL", start_date=date(2020, 1, 1), limit=500)

awards = USAspendingAdapter(USASpendingClient()).fetch(
    start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), limit=50
)
```

Quiver endpoint paths, auth header/prefix, response envelope, record ID and source URL fields depend on current provider documentation and account access. Configure those explicitly; do not assume endpoint paths or scrape undocumented routes:

```python
from market_recon.sources.quiver import QuiverAdapter

adapter = QuiverAdapter(
    endpoint_url="https://<documented-endpoint>",
    api_key=os.environ["QUIVER_API_KEY"],
    auth_header="<documented-header>",
    auth_prefix="<documented-prefix>",
    results_key="<documented-results-field>",
    id_field="<documented-record-id-field>",
)
records = adapter.fetch(params={})
```

The placeholders are intentional: verify the current API docs and subscription permissions before providing real values. The adapter sends one bounded GET request and does not implement undocumented pagination.
