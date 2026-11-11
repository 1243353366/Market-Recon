from __future__ import annotations

from market_recon.sources.sec_parser import html_to_text, parse_10k_10q


def test_parse_10k_sections_prefers_full_body_over_contents_entry() -> None:
    text = """PART I
ITEM 1. BUSINESS
Business
ITEM 1A. RISK FACTORS
Risks
PART II
ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS
MD&A body with revenue discussion and operating results.
ITEM 8. FINANCIAL STATEMENTS
Statements body.
PART I
ITEM 1. BUSINESS
The company designs and sells products across multiple markets. This is a longer body than the contents entry.
ITEM 1A. RISK FACTORS
Risks include competition, regulation, and supply constraints. More details follow.
PART II
ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS
Revenue increased during the year. Operating expenses also increased, and management discussed liquidity.
ITEM 8. FINANCIAL STATEMENTS
Consolidated financial statements follow.
"""
    parsed = parse_10k_10q(text, "10-K")
    assert parsed.form == "10-K"
    assert "designs and sells" in parsed.sections["Part I Item 1"]
    assert "competition" in parsed.sections["Part I Item 1A"]
    assert "Revenue increased" in parsed.sections["Part II Item 7"]
    assert "Consolidated financial" in parsed.sections["Part II Item 8"]


def test_parse_10q_preserves_part_and_item() -> None:
    parsed = parse_10k_10q("PART I\nITEM 2. MANAGEMENT'S DISCUSSION\nQuarterly results and liquidity.\nPART II\nITEM 1A. RISK FACTORS\nNo material changes.", "10-Q")
    assert "Quarterly results" in parsed.sections["Part I Item 2"]
    assert "No material changes" in parsed.sections["Part II Item 1A"]


def test_parser_rejects_unsupported_form_and_keeps_full_text() -> None:
    try:
        parse_10k_10q("some text", "8-K")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected unsupported form error")
    assert "Quarterly" in parse_10k_10q("PART I\nITEM 2. Quarterly", "10-Q").full_text


def test_html_to_text_removes_scripts_and_preserves_text() -> None:
    text = html_to_text("<html><script>bad()</script><p>Item 1. Business</p><p>Good content</p></html>")
    assert "Good content" in text
    assert "bad()" not in text
