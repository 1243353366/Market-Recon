from __future__ import annotations

from market_recon.sources.filing_diff import FilingVersion
from market_recon.sources.filing_intelligence import summarize_filing_changes


def filing(form: str, date: str, url: str, sections: dict[str, str]) -> FilingVersion:
    return FilingVersion("000123", form, date, url, sections)


def test_surfaces_new_and_removed_risks_with_both_citations():
    older = filing("10-K", "2025-02-01", "https://www.sec.gov/old", {"Part I Item 1A": "Risk factor A\nThe company faces supplier concentration risk."})
    newer = filing("10-K", "2026-02-01", "https://www.sec.gov/new", {"Part I Item 1A": "Risk factor A\nA new cybersecurity risk could adversely affect operations."})
    results = summarize_filing_changes(older, newer)
    assert [item.change for item in results["risks"]] == ["new", "removed"]
    assert all(item.before_url.endswith("old") and item.after_url.endswith("new") for item in results["risks"])


def test_surfaces_exec_comp_supply_chain_and_litigation_changes():
    older = filing("DEF 14A", "2025-01-01", "https://www.sec.gov/proxy-old", {
        "Item 10": "The chief financial officer is Jane Doe.",
        "Item 11": "Annual bonus is based on revenue growth.",
        "Item 1A": "We rely on suppliers for key components. A lawsuit is pending in state court.",
    })
    newer = filing("DEF 14A", "2026-01-01", "https://www.sec.gov/proxy-new", {
        "Item 10": "The chief financial officer resigned; a successor was appointed.",
        "Item 11": "The compensation committee adopted a new equity award and incentive plan.",
        "Item 1A": "We rely on suppliers for key components. A settlement resolved the lawsuit.",
    })
    results = summarize_filing_changes(older, newer)
    assert results["executive_changes"]
    assert results["compensation_changes"]
    assert results["litigation_changes"]
    assert any("supplier" in item.text.lower() for item in results["supply_chain_changes"])
    assert all(item.before_url and item.after_url for group in results.values() for item in group)


def test_same_filing_form_and_company_required():
    before = filing("10-K", "2025-01-01", "https://www.sec.gov/a", {})
    other = FilingVersion("2", "10-K", "2026-01-01", "https://www.sec.gov/b", {})
    try:
        summarize_filing_changes(before, other)
    except ValueError as exc:
        assert "different CIKs" in str(exc)
    else:
        raise AssertionError("Expected CIK mismatch")
