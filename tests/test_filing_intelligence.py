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


def test_adversarial_unrelated_changes_in_broad_sections_do_not_produce_false_positives():
    """Adversarial check: changes in Item 1, Item 1A, or Item 7 discussing general business,
    accounting, or marketing must not trigger supply chain, litigation, or executive findings.
    """
    older = filing("10-K", "2025-02-01", "https://www.sec.gov/old-10k", {
        "Part I Item 1": "Our business primarily provides enterprise cloud software and subscription services.\nWe operate across three commercial geographic regions.",
        "Part I Item 1A": "We face macroeconomic uncertainty in European consumer markets.\nCurrency fluctuations could impact our international operations.",
        "Part II Item 7": "Revenue increased by 14% primarily due to higher cloud adoption.\nGross margin expanded by 120 basis points reflecting software mix.",
    })
    newer = filing("10-K", "2026-02-01", "https://www.sec.gov/new-10k", {
        "Part I Item 1": "Our business primarily provides enterprise cloud software, generative AI solutions, and subscription services.\nWe operate across four commercial geographic regions including Latin America.",
        "Part I Item 1A": "We face macroeconomic uncertainty in global commercial markets.\nWe adopted standard guidance regarding lease accounting under ASC 842.",
        "Part II Item 7": "Revenue increased by 18% primarily due to higher cloud and AI adoption.\nGross margin expanded by 150 basis points reflecting favorable enterprise software mix.",
    })
    results = summarize_filing_changes(older, newer)

    # None of these changes contain supply chain keywords (supplier, vendor, manufacturing, logistics, etc.)
    # Under the previous bug, all changed lines in Item 1, Item 1A, and Item 7 were mislabeled as supply_chain_changes!
    assert len(results["supply_chain_changes"]) == 0, (
        f"Expected 0 supply chain findings on unrelated text, got {results['supply_chain_changes']}"
    )
    # None of these changes contain litigation keywords
    assert len(results["litigation_changes"]) == 0
    # None of these changes contain executive changes keywords
    assert len(results["executive_changes"]) == 0
    # None of these changes contain compensation keywords
    assert len(results["compensation_changes"]) == 0


def test_section_and_phrase_match_reports_detailed_reason():
    older = filing("10-K", "2025-02-01", "https://www.sec.gov/old", {
        "Part II Item 7": "Our inventory levels remained stable throughout the fiscal year.",
    })
    newer = filing("10-K", "2026-02-01", "https://www.sec.gov/new", {
        "Part II Item 7": "Our vendor inventory and component logistics faced material capacity constraints.",
    })
    results = summarize_filing_changes(older, newer)
    findings = results["supply_chain_changes"]
    assert len(findings) == 2  # 1 removed, 1 new
    new_finding = next(f for f in findings if f.change == "new")
    assert new_finding.matched_section_hint is True
    assert new_finding.matched_phrase in ("vendor", "inventory", "component", "logistics", "capacity constraint")
    assert "phrase" in new_finding.match_reason and "relevant section" in new_finding.match_reason
    assert new_finding.analyst_status == "unreviewed"
