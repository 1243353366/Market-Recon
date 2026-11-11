from __future__ import annotations

from market_recon.sources.filing_diff import FilingVersion, compare_filing_versions


def version(cik: str, filing_date: str, url: str, sections: dict[str, str], form: str = "10-K") -> FilingVersion:
    return FilingVersion(cik=cik, form=form, filing_date=filing_date, source_url=url, sections=sections)


def test_unchanged_sections_are_omitted_and_changed_text_cited() -> None:
    before = version("0000123", "2025-02-01", "https://sec.gov/old", {"Item 1A": "Risk factor A", "Item 7": "Revenue was stable."})
    after = version("123", "2026-02-01", "https://sec.gov/new", {"Item 1A": "Risk factor A\nNew export control risk.", "Item 7": "Revenue was stable."})
    changes = compare_filing_versions(before, after)
    assert len(changes) == 1
    assert changes[0].section == "Item 1A"
    assert changes[0].status == "changed"
    assert "New export control risk" in changes[0].unified_diff
    assert changes[0].before_url.endswith("old")
    assert changes[0].after_url.endswith("new")


def test_section_additions_and_removals() -> None:
    before = version("1", "2025-01-01", "https://sec.gov/a", {"Item 1": "Business", "Item 2": "Old"})
    after = version("1", "2026-01-01", "https://sec.gov/b", {"Item 1": "Business", "Item 3": "New"})
    changes = {item.section: item.status for item in compare_filing_versions(before, after)}
    assert changes == {"Item 2": "removed", "Item 3": "added"}


def test_comparison_rejects_mismatched_cik_form_and_bad_limits() -> None:
    before = version("1", "2025-01-01", "https://sec.gov/a", {})
    assert before
    try:
        compare_filing_versions(before, version("2", "2026-01-01", "https://sec.gov/b", {}))
    except ValueError as exc:
        assert "different CIKs" in str(exc)
    else:
        raise AssertionError("Expected CIK validation")
    try:
        compare_filing_versions(before, version("1", "2026-01-01", "https://sec.gov/b", {}, "10-Q"))
    except ValueError as exc:
        assert "different base filing forms" in str(exc)
    else:
        raise AssertionError("Expected form validation")
    try:
        compare_filing_versions(before, before, excerpt_chars=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected excerpt validation")
