from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

import requests

from market_recon.sources.sec_parser import html_to_text

from .models import SourceDocument

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"


class SecEdgarClient:
    """Small SEC EDGAR collector with explicit identity and bounded request timeouts."""

    def __init__(self, user_agent: str, timeout: int = 30) -> None:
        if not user_agent or "@" not in user_agent:
            raise ValueError("Set SEC_USER_AGENT to an identifying application name and contact email")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.session = requests.Session()
        # Do not hard-code Host: requests must route each SEC endpoint to its own host.
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self.timeout = timeout

    def find_cik(self, ticker: str) -> str:
        response = self.session.get(SEC_TICKERS_URL, timeout=self.timeout)
        response.raise_for_status()
        wanted = ticker.strip().upper()
        for record in response.json().values():
            if str(record.get("ticker", "")).upper() == wanted:
                return str(record["cik_str"]).zfill(10)
        raise LookupError(f"Ticker not found in SEC company tickers list: {ticker}")

    def recent_filings(self, ticker: str, forms: set[str] | None = None, limit: int = 20) -> list[SourceDocument]:
        if limit < 1:
            raise ValueError("limit must be positive")
        cik = self.find_cik(ticker)
        response = self.session.get(SEC_SUBMISSIONS_URL.format(cik=cik), timeout=self.timeout)
        response.raise_for_status()
        recent = response.json().get("filings", {}).get("recent", {})
        columns = ("accessionNumber", "filingDate", "form", "primaryDocument")
        row_count = min((len(recent.get(column, [])) for column in columns), default=0)
        docs: list[SourceDocument] = []
        for index in range(row_count):
            accession, filed, form, filename = (recent[column][index] for column in columns)
            if forms and form not in forms or not accession or not filename:
                continue
            url = SEC_ARCHIVES_URL.format(
                cik=str(int(cik)), accession=accession.replace("-", ""), filename=filename
            )
            filing_response = self.session.get(url, timeout=self.timeout)
            if filing_response.status_code == 404:
                continue
            filing_response.raise_for_status()
            text = html_to_text(filing_response.content)
            if not text:
                continue
            document_id = sha256(f"sec:{cik}:{accession}:{filename}".encode()).hexdigest()
            docs.append(SourceDocument(
                document_id=document_id,
                title=f"{ticker.upper()} {form} filed {filed}",
                text=text,
                source_name="SEC EDGAR",
                source_url=url,
                document_type=form,
                published_at=filed,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                ticker=ticker.upper(),
                cik=cik,
                metadata={"accession_number": accession},
            ))
            if len(docs) >= limit:
                break
        return docs


def filing_forms() -> set[str]:
    return {"10-K", "10-Q", "8-K", "DEF 14A", "3", "4", "5", "144", "13F-HR"}
