"""Guard against collection identifier drift between the registry and the adapters."""
from __future__ import annotations

import ast
from pathlib import Path

from market_recon.sources.collections import COLLECTIONS
from market_recon.sources.sec_edgar import SEC_COLLECTIONS, collection_for_form

SOURCES = Path(__file__).resolve().parents[1] / "market_recon" / "sources"
REGISTERED = frozenset(definition.collection_id for definition in COLLECTIONS)


def emitted_collection_literals() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in sorted(SOURCES.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg == "collection" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    found.setdefault(keyword.value.value, set()).add(path.name)
    return found


def test_registry_ids_are_unique() -> None:
    ids = [definition.collection_id for definition in COLLECTIONS]
    assert len(ids) == len(set(ids))


def test_adapters_emit_registered_collections() -> None:
    literals = emitted_collection_literals()
    assert literals, "no collection literals found; the guard would be vacuous"
    unregistered = {value: sorted(files) for value, files in literals.items() if value not in REGISTERED}
    assert not unregistered, f"adapters emit collections absent from the registry: {unregistered}"


def test_sec_form_map_uses_registered_collections() -> None:
    assert set(SEC_COLLECTIONS) <= REGISTERED, f"unregistered SEC collections: {sorted(set(SEC_COLLECTIONS) - REGISTERED)}"
    for forms in SEC_COLLECTIONS.values():
        for form in forms:
            assert collection_for_form(form) in REGISTERED
    assert collection_for_form("NT 10-K") in REGISTERED
