# Public Signal Intelligence (MVP)

Market Recon now has a small, evidence-preserving cross-signal analysis layer. It accepts normalized public observations, requires an HTTPS source URL for every record, groups by a resolved entity ID and lookback window, and flags mixed positive/negative observations from distinct signal categories for human review.

## What it does not do

- It does not collect data from ImportYeti, MarineTraffic, FreightWaves, LinkedIn, GitHub, patent databases, or government systems. The catalog marks these as planned or requiring source/terms review.
- It does not infer deception, causation, alpha, company quality, or future returns.
- It does not rank or recommend securities.
- A signal's `positive` or `negative` direction describes the direction of a documented change relative to a stated baseline, not whether that observation is good or bad for a stock.
- It does not bypass login, paywalls, access controls, rate limits, or licensing restrictions. Use official APIs/open datasets or licensed access and honor terms.

## Signal model

Each signal contains a stable entity identifier, observation date, type, direction, summary, source name, source URL, and optional metric/baseline/confidence. Avoid matching entities on name alone. Keep source records and the derived signal separate; document the transformation and time period.

## Usage

```python
from datetime import date
from market_recon.intelligence import PublicSignal, find_cross_signal_divergences

signals = [
    PublicSignal(
        signal_id="source-record-1", entity_id="CIK0000000001", entity_name="Example Co",
        kind="management_demand_commentary", direction="negative", observed_on=date(2026, 1, 10),
        summary="Management described demand as soft in the quarterly call.",
        source_name="Company earnings call", source_url="https://example.org/transcript",
        baseline="prior-quarter wording; qualitative, manually reviewed", confidence=0.6,
    ),
    PublicSignal(
        signal_id="source-record-2", entity_id="CIK0000000001", entity_name="Example Co",
        kind="hiring_activity", direction="positive", observed_on=date(2026, 1, 20),
        summary="Relevant public job postings increased versus the prior 30-day snapshot.",
        source_name="Company careers page", source_url="https://example.org/careers",
        metric_name="active_posting_count", metric_value=18, unit="roles",
        baseline="prior 30-day snapshot; duplicate and expired postings removed", confidence=0.5,
    ),
]
for finding in find_cross_signal_divergences(signals, as_of=date(2026, 2, 1)):
    print(finding.entity_name, finding.interpretation)
    for item in finding.signals:
        print(item.observed_on, item.kind, item.direction, item.source_url)
```

This simple MVP reports only mixed signal clusters. It is not a statistical anomaly detector and does not normalize different time periods, source coverage, seasonality, reporting lags, or entity resolution. Interpret every signal in context, investigate missing/disconfirming evidence, and verify source records before drawing conclusions.

## Planned source families

- Supply chain: official port datasets, shipping/shipment datasets where licensed, public company disclosures.
- Hiring: company career pages and authorized job APIs; snapshot changes can reflect duplicate, expired, or syndicated postings.
- Open source: public GitHub/GitLab repository activity, only where project/company attribution is verifiable; activity is not a reliable proxy for product release or revenue.
- Patents: USPTO, WIPO, and public patent publications; filings indicate claims, not necessarily commercial products.
- Government spending: USAspending.gov and SAM.gov official public records; awards/obligations are not equivalent to recognized company revenue.
- Executive/regulatory: SEC proxies and filings, Congress.gov, and official agency releases.
- Customer sentiment: public review sources subject to terms; samples are biased and should not be treated as representative.

Each integration requires a source-specific data dictionary, update cadence, terms/license check, retention policy, and tests for missingness and revisions before being used in analysis.
