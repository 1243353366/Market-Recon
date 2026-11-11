from __future__ import annotations

from market_recon.coach.agent import InvestorContext, assess_readiness, classify_topic, coach


def test_topic_routing() -> None:
    assert classify_topic("How does diversification work with index funds?") == "diversification"
    assert classify_topic("Should I trade during a market crash?") == "market_timing"


def test_context_is_reflection_not_recommendation() -> None:
    context = InvestorContext(emergency_reserve_ready=False, high_interest_debt=True, time_horizon="long term")
    notes = assess_readiness(context)
    assert len(notes) == 3
    reply = coach("How do I get started?", context)
    assert "not a personalized recommendation" in reply.message
    assert reply.sources
    assert "citation_attacher" in reply.tools_used


def test_specific_stock_request_does_not_name_a_security() -> None:
    reply = coach("Which stock should I buy?")
    assert reply.topic == "stock_picking"
    assert "will not tell you which stock to buy or sell" in reply.message
