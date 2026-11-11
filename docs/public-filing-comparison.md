# Public filing version comparison

Market Recon's timing-gap work should compare public filing versions, not speculate about undisclosed information. `market_recon.sources.filing_diff` provides a deterministic helper that compares already-parsed 10-K/10-Q sections for the same CIK and base form.

Example:

```python
from market_recon.sources.filing_diff import FilingVersion, compare_filing_versions

older = FilingVersion("0000123456", "10-K", "2025-02-01", "https://www.sec.gov/Archives/edgar/data/.../old.htm", {"Part I Item 1A": "Prior risk text"})
newer = FilingVersion("0000123456", "10-K", "2026-02-01", "https://www.sec.gov/Archives/edgar/data/.../new.htm", {"Part I Item 1A": "Updated risk text"})
for change in compare_filing_versions(older, newer):
    print(change.section, change.status, change.unified_diff)
    print("Before:", change.before_url)
    print("After:", change.after_url)
```

The comparator omits unchanged sections, reports added/removed/changed text, and retains citations to both filing versions. Similarity is a textual ratio only, not a risk or materiality score. TOC differences, formatting, amendments, and parser errors can create misleading diffs; review originals before interpreting changes. It does not assert that a change is important or predict business outcomes.

Next research steps can compare DEF 14A versions for compensation, board, and equity-plan text using the same evidence-first pattern. SEC filing text should be parsed from official public sources, retain accession IDs, and obey SEC fair-access guidance. No use of leaked, exposed, confidential, or access-restricted information is supported.
