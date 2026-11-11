from __future__ import annotations

from typing import Any

from market_recon.rag.sec_edgar import SecEdgarClient
from .schema import NormalizedRecord, SourceAdapter, utc_now_iso

SEC_COLLECTIONS = {
    "filings": {"10-K", "10-Q", "8-K", "S-1", "DEF 14A", "SC 13D", "SC 13G"},
    "insider": {"3", "4", "5"},
    "institutional_holdings": {"13F-HR"},
    "resale_notices": {"144"},
}


def collection_for_form(form: str) -> str:
    for collection, forms in SEC_COLLECTIONS.items():
        if form in forms:
            return collection
    return "other_sec_filings"


class SECEdgarAdapter:
    source_id = "sec_edgar"

    def __init__(self, client: SecEdgarClient) -> None:
        self.client = client

    def fetch(self, *, ticker: str, forms: set[str] | None = None, limit: int = 20, **_: Any) -> list[NormalizedRecord]:
        documents = self.client.recent_filings(ticker=ticker, forms=forms, limit=limit)
        records: list[NormalizedRecord] = []
        retrieved = utc_now_iso()
        for document in documents:
            accession = str(document.metadata.get("accession_number", document.document_id))
            record_id = f"sec:{document.cik}:{accession}"
            records.append(NormalizedRecord(
                record_id=record_id,
                source_id=self.source_id,
                collection=collection_for_form(document.document_type),
                record_type="sec_filing",
                source_name=document.source_name,
                source_url=document.source_url,
                retrieved_at=retrieved,
                data={"title": document.title, "text": document.text, **document.metadata},
                observed_at=document.published_at,
                published_at=document.published_at,
                entity_id=f"CIK{document.cik}" if document.cik else None,
                entity_name=None,
                ticker=document.ticker,
                cik=document.cik,
                license_status="public_source_terms_review_required",
                metadata={"form": document.document_type},
            ))
        return records
