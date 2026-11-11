# Filing change intelligence

Market Recon now includes a transparent rule-based review layer on top of parsed filing section diffs. It can surface candidate:

- new and removed risk language
- executive/board changes
- compensation changes
- supply-chain changes
- litigation/legal-proceeding changes

## Usage

```python
from market_recon.sources.filing_diff import FilingVersion
from market_recon.sources.filing_intelligence import summarize_filing_changes

older = FilingVersion("0000123456", "10-K", "2025-02-01", "https://www.sec.gov/Archives/edgar/data/.../old.htm", {
    "Part I Item 1A": "Prior risk factor text."
})
newer = FilingVersion("0000123456", "10-K", "2026-02-01", "https://www.sec.gov/Archives/edgar/data/.../new.htm", {
    "Part I Item 1A": "Updated risk factor text."
})
for category, findings in summarize_filing_changes(older, newer).items():
    print(category)
    for finding in findings:
        print(finding.change, finding.section, finding.text)
        print(finding.before_url, finding.after_url)
```

This uses line-level text differences and explicit keyword/section rules. It is an **assistive review queue**, not a complete semantic classifier: it may miss reworded concepts, flag boilerplate, or be affected by parser quality and filing formatting. “Removed” means text absent from the compared parsed sections; it does not prove a risk has ended. Executive, compensation, supply-chain, and litigation labels are candidate matches only, not verified events or legal conclusions. Verify every excerpt against both linked filings.

The tool reports source URLs, dates, section, category, change type, and matched text. It does not score companies, rank securities, infer intent, or provide investment advice. It is suitable for 10-K/10-Q comparisons and can be used with parsed proxy (`DEF 14A`) sections when `FilingVersion` is extended to allow that form; current `FilingVersion` validation supports only 10-K/10-Q and their amendments.
