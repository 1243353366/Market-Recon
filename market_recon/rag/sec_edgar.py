from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

import requests
from bs4 import BeautifulSoup

from .models import SourceDocument

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"


class SecEdgarClient:
    """Small SEC EDGAR collector. Set SEC_USER_AGENT to an identifying contact string."""

    def __init__(self, user_agent: str, timeout: int = 30) -> None:
        if not user_agent or "@" not in user_agent:
            raise ValueError("SEC requires a descriptive User-Agent with contact information; set SEC_USER_AGENT")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"})
        self.timeout = timeout

    def find_cik(self, ticker: str) -> str:
        response = self.session.get(SEC_TICKERS_URL, timeout=self.timeout)
        response.raise_for_status()
        for record in response.json().values():
            if record.get("ticker", "").upper() == ticker.upper():
                return str(record["cik_str"]).zfill(10)
        raise LookupError(f"Ticker not found in SEC company tickers list: {ticker}")

    def recent_filings(self, ticker: str, forms: set[str] | None = None, limit: int = 20) -> list[SourceDocument]:
        cik = self.find_cik(ticker)
        response = self.session.get(SEC_SUBMISSIONS_URL.format(cik=cik), timeout=self.timeout)
        response.raise_for_status()
        recent = response.json().get("filings", {}).get("recent", {})
        rows = zip(recent.get("accessionNumber", []), recent.get("filingDate", []),
                   recent.get("form", []), recent.get("primaryDocument", []), strict=False)
        docs: list[SourceDocument] = []
        for accession, filed, form, filename in rows:
            if forms and form not in forms:
                continue
            if not filename or not accession:
                continue
            accession_path = accession.replace("-", "")
            cik_path = str(int(cik))
            url = SEC_ARCHIVES_URL.format(cik=cik_path, accession=accession_path, filename=filename)
            filing_response = self.session.get(url, timeout=self.timeout)
            if filing_response.status_code != 200:
                continue
            soup = BeautifulSoup(filing_response.content, "html.parser")
            for node in soup(["script", "style", "ix:header"]):
                node.decompose()
            text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
            if not text:
                continue
            doc_id = sha256(f"sec:{cik}:{accession}:{filename}".encode()).hexdigest()
            docs.append(SourceDocument(
                document_id=doc_id,
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
