from __future__ import annotations

from market_recon.investor_library import categories, load_investors, search_investors


def test_catalog_has_50_unique_profiles() -> None:
    records = load_investors()
    assert len(records) == 50
    assert len({record["id"] for record in records}) == 50


def test_strategy_search_and_category_filter() -> None:
    assert any(item["name"] == "Warren Buffett" for item in search_investors("decades"))
    assert all(item["category"] == "Index investing" for item in search_investors("", "Index investing"))
    assert len(categories()) >= 7
