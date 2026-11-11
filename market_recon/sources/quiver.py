from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests

from .schema import NormalizedRecord, utc_now_iso


class QuiverAdapter:
    """Configurable REST adapter; intentionally does not assume undocumented endpoint paths.

    Supply the exact endpoint and response mapping from the account's current Quiver
    documentation/plan. This avoids baking in endpoint, auth-header, or response-shape
    assumptions. It performs one bounded request; pagination is caller-controlled.
    """

    source_id = "quiver_quant"

    def __init__(
        self,
        *,
        endpoint_url: str,
        api_key: str,
        auth_header: str = "Authorization",
        auth_prefix: str = "",
        results_key: str = "data",
        id_field: str = "id",
        source_url_field: str = "url",
        record_type: str = "quiver_record",
        collection: str = "alternative_data",
        session: requests.Session | None = None,
        timeout: float = 20,
    ) -> None:
        parsed = urlparse(endpoint_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("endpoint_url must be an absolute HTTPS URL")
        if not api_key.strip():
            raise ValueError("Quiver API key is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.auth_header = auth_header
        self.auth_prefix = auth_prefix
        self.results_key = results_key
        self.id_field = id_field
        self.source_url_field = source_url_field
        self.record_type = record_type
        self.collection = collection
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch(self, *, params: dict[str, Any] | None = None, **_: Any) -> list[NormalizedRecord]:
        response = self.session.get(
            self.endpoint_url,
            params=params or {},
            headers={self.auth_header: f"{self.auth_prefix}{self.api_key}"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        body = response.json()
        rows = body.get(self.results_key) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            raise ValueError(f"Expected a list in response field {self.results_key!r}")
        retrieved = utc_now_iso()
        records: list[NormalizedRecord] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            provider_id = row.get(self.id_field)
            if provider_id is None:
                raise ValueError(f"Quiver result missing configured ID field {self.id_field!r} at index {index}")
            cited_url = row.get(self.source_url_field)
            if not isinstance(cited_url, str) or not cited_url.startswith("https://"):
                # API endpoint is cited as retrieval provenance; provider payload is retained
                # so downstream review can determine whether a better source citation exists.
                cited_url = self.endpoint_url
            records.append(NormalizedRecord(
                record_id=f"quiver:{provider_id}",
                source_id=self.source_id,
                collection=self.collection,
                record_type=self.record_type,
                source_name="Quiver Quantitative (third-party aggregation)",
                source_url=cited_url,
                retrieved_at=retrieved,
                observed_at=str(row["date"]) if row.get("date") is not None else None,
                data=row,
                entity_name=str(row.get("company") or row.get("ticker") or "") or None,
                ticker=str(row["ticker"]).upper() if row.get("ticker") else None,
                license_status="provider_terms_and_plan_review_required",
                metadata={"api_endpoint": self.endpoint_url},
            ))
        return records
