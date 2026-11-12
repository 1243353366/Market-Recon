from __future__ import annotations

from market_recon.sources.entity_resolution import EntityResolver, normalize_entity_name


def test_normalize_entity_name_strips_legal_suffixes():
    assert normalize_entity_name("Apple Inc.") == "apple"
    assert normalize_entity_name("Microsoft Corporation") == "microsoft"
    assert normalize_entity_name("NVIDIA Corp") == "nvidia"
    assert normalize_entity_name("Amazon.com, Inc.") == "amazon com"


def test_resolver_prioritizes_stable_cik_identifier():
    resolver = EntityResolver()
    resolver.register("entity:sec:0000320193", "Apple Inc.", ticker="AAPL", cik="0000320193")

    result = resolver.resolve(name="Apple Computer", cik="320193")
    assert result.is_resolved is True
    assert result.match_method == "exact_cik"
    assert result.entity_id == "entity:sec:0000320193"
    assert result.confidence == 1.0
    assert result.status == "confirmed"
    assert result.stable_identifiers["cik"] == "0000320193"


def test_resolver_matches_registered_ticker():
    resolver = EntityResolver()
    resolver.register("entity:sec:0001045810", "NVIDIA Corporation", ticker="NVDA", cik="0001045810")

    result = resolver.resolve(name="NVIDIA Corp", ticker="NVDA")
    assert result.is_resolved is True
    assert result.match_method == "exact_ticker"
    assert result.entity_id == "entity:sec:0001045810"
    assert result.canonical_name == "NVIDIA Corporation"


def test_resolver_uses_government_recipient_id():
    resolver = EntityResolver()
    result = resolver.resolve(name="Lockheed Martin Co", recipient_id="UEI123456789")
    assert result.is_resolved is True
    assert result.match_method == "exact_recipient_id"
    assert result.entity_id == "entity:gov:UEI123456789"
    assert result.status == "confirmed"


def test_resolver_rejects_forced_linking_on_ambiguous_generic_names():
    resolver = EntityResolver()
    # Generic names with no CIK/ticker must remain unresolved rather than creating false links
    generic_cases = ["Capital Inc", "Holdings LLC", "Management Group", "Enterprises Co"]
    for generic in generic_cases:
        result = resolver.resolve(name=generic)
        assert result.is_resolved is False
        assert result.status == "unresolved"
        assert result.entity_id is None
        assert result.confidence == 0.0


def test_resolver_handles_unregistered_unknown_entity():
    resolver = EntityResolver()
    result = resolver.resolve(name="Completely Unknown Stealth Venture")
    assert result.is_resolved is False
    assert result.status == "unresolved"
    assert result.entity_id is None
