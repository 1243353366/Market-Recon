from __future__ import annotations

import json
from datetime import date
from typing import Any

from market_recon.data_sources_api import FredClient, USASpendingClient
from market_recon.rag.sec_edgar import SecEdgarClient
from market_recon.sources.fred import FREDAdapter
from market_recon.sources.quiver import QuiverAdapter
from market_recon.sources.sec_edgar import SECEdgarAdapter
from market_recon.sources.stooq import StooqAdapter
from market_recon.sources.usaspending import USAspendingAdapter
from market_recon.sources.yahoo_finance import YahooFinanceAdapter
from market_recon.sources.schema import SourceAdapter


def _env(config: dict[str, Any], key: str, default: str = "") -> str:
    env_name = str(config.get(key, ""))
    return __import__("os").environ.get(env_name, default) if env_name else default


def load_source_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as source:
        config = json.load(source)
    if not isinstance(config, dict) or not isinstance(config.get("sources"), dict):
        raise ValueError("Source config must be a JSON object with a 'sources' mapping")
    return config


def load_adapters(path: str) -> dict[str, SourceAdapter]:
    """Instantiate enabled adapters from JSON config; secrets are read only from env vars."""
    config = load_source_config(path)
    adapters: dict[str, SourceAdapter] = {}
    for source_id, options in config["sources"].items():
        if not isinstance(options, dict) or not options.get("enabled", False):
            continue
        timeout = float(options.get("timeout", 30))
        if source_id == "sec_edgar":
            adapters[source_id] = SECEdgarAdapter(SecEdgarClient(_env(options, "user_agent_env"), timeout=int(timeout)))
        elif source_id == "fred":
            adapters[source_id] = FREDAdapter(FredClient(_env(options, "api_key_env"), timeout=timeout))
        elif source_id == "usaspending":
            adapters[source_id] = USAspendingAdapter(USASpendingClient(timeout=timeout))
        elif source_id == "quiver_quant":
            adapters[source_id] = QuiverAdapter(
                endpoint_url=str(options["endpoint_url"]),
                api_key=_env(options, "api_key_env"),
                auth_header=str(options.get("auth_header", "Authorization")),
                auth_prefix=str(options.get("auth_prefix", "")),
                results_key=str(options.get("results_key", "data")),
                id_field=str(options.get("id_field", "id")),
                source_url_field=str(options.get("source_url_field", "url")),
                record_type=str(options.get("record_type", "quiver_record")),
                collection=str(options.get("collection", "alternative_data")),
                timeout=timeout,
            )
        elif source_id == "yahoo_finance":
            adapters[source_id] = YahooFinanceAdapter(timeout=timeout)
        elif source_id == "stooq":
            adapters[source_id] = StooqAdapter(timeout=timeout)
        else:
            raise ValueError(f"Unknown source adapter: {source_id}")
    return adapters
