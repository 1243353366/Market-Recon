"""The filing workflow's extraction path must drop hidden Inline XBRL facts."""
from __future__ import annotations

from market_recon.rag.sec_edgar import SEC_ARCHIVES_URL, SEC_SUBMISSIONS_URL, SEC_TICKERS_URL, SecEdgarClient

FILING_HTML = b"""
<html><body>
<div style="display:none"><ix:hidden>
<ix:nonfraction name="dei:EntityRegistrantName">HIDDEN-FACT-VALUE</ix:nonfraction>
</ix:hidden></div>
<ix:header><ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric></ix:header>
<p>Item 1A. Risk Factors</p>
<p>Visible supplier concentration risk.</p>
<script>var secret = "SCRIPT-NOISE";</script>
</body></html>
"""


class FakeResponse:
    def __init__(self, *, payload=None, content: bytes = b"", status_code: int = 200) -> None:
        self._payload = payload
        self.content = content
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"unexpected status {self.status_code}")


class FakeSession:
    def get(self, url: str, timeout: int = 30):  # noqa: ARG002
        if url == SEC_TICKERS_URL:
            return FakeResponse(payload={"0": {"ticker": "DEMO", "cik_str": 123}})
        if url == SEC_SUBMISSIONS_URL.format(cik="0000000123"):
            return FakeResponse(payload={"filings": {"recent": {
                "accessionNumber": ["0000-26-000001"],
                "filingDate": ["2026-02-01"],
                "form": ["10-K"],
                "primaryDocument": ["demo-10k.htm"],
            }}})
        if url == SEC_ARCHIVES_URL.format(cik="123", accession="000026000001", filename="demo-10k.htm"):
            return FakeResponse(content=FILING_HTML)
        raise AssertionError(f"unexpected URL {url}")


def client() -> SecEdgarClient:
    instance = SecEdgarClient("market-recon-test test@example.com")
    instance.session = FakeSession()
    return instance


def test_hidden_xbrl_facts_and_script_noise_are_removed() -> None:
    documents = client().recent_filings("DEMO", {"10-K"}, 1)
    assert len(documents) == 1
    text = documents[0].text
    assert "Visible supplier concentration risk." in text
    assert "HIDDEN-FACT-VALUE" not in text
    assert "SCRIPT-NOISE" not in text


def test_extraction_matches_the_parser_helper() -> None:
    from market_recon.sources.sec_parser import html_to_text

    documents = client().recent_filings("DEMO", {"10-K"}, 1)
    assert documents[0].text == html_to_text(FILING_HTML)
