from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InvestorContext:
    """Optional self-reported context; deliberately excludes account balances and identifiers."""

    goal: str = ""
    time_horizon: str = ""
    emergency_reserve_ready: bool | None = None
    high_interest_debt: bool | None = None
    investing_experience: str = ""
    country_or_region: str = ""

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "InvestorContext":
        allowed = {field for field in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in values.items() if key in allowed})


@dataclass(frozen=True)
class CoachReply:
    topic: str
    message: str
    next_step: str
    sources: tuple[tuple[str, str], ...]
    tools_used: tuple[str, ...]


EDUCATION: dict[str, dict[str, str]] = {
    "getting_started": {
        "message": (
            "A durable starting point is a repeatable process: understand your goals and time horizon, "
            "keep a suitable cash reserve, address costly debt, learn how diversification and fees work, "
            "and invest only money you can leave invested through market declines. Many investors study "
            "broad, low-cost index funds as one diversified approach; that is an educational example, "
            "not a recommendation to buy a particular fund."
        ),
        "next": "Which would be most useful to learn about first: risk, diversification, fees, or account types?",
    },
    "emergency_reserve": {
        "message": (
            "An emergency reserve can reduce the chance of needing to sell investments at an inconvenient "
            "time. The appropriate amount depends on circumstances such as income stability, obligations, "
            "and access to other resources. Consider learning how liquid savings and investing serve different roles."
        ),
        "next": "Would you like a checklist for thinking through cash-flow resilience (without sharing dollar amounts)?",
    },
    "debt": {
        "message": (
            "Debt costs and investment returns are uncertain in different ways. Understanding the interest "
            "rate, fees, repayment terms, and any penalties can help you compare priorities. Paying down "
            "high-cost debt may be worth evaluating before taking more investment risk; the best choice "
            "depends on your full situation."
        ),
        "next": "You can compare the debt's guaranteed cost with the uncertain nature of market returns; avoid posting account or loan details here.",
    },
    "diversification": {
        "message": (
            "Diversification means spreading exposure across investments so results depend less on any one "
            "company or sector. It can reduce some company-specific risks, but it cannot prevent broad-market "
            "losses. Broad index funds are one way people study diversification; indexes differ in coverage, "
            "fees, concentration, and risk."
        ),
        "next": "When comparing an investment approach, examine what it owns, how concentrated it is, its fees, and what risks remain.",
    },
    "long_term_habits": {
        "message": (
            "Regular investing can make the process more consistent, while avoiding frequent trading may "
            "reduce costs and impulsive decisions. Returns are never guaranteed, and investing regularly "
            "does not prevent losses. A written plan, review schedule, and rules for when not to act can help "
            "keep decisions deliberate."
        ),
        "next": "Choose a review cadence and write down what would justify changing your plan before markets get stressful.",
    },
    "account_types": {
        "message": (
            "Tax-advantaged account rules, eligibility, contribution limits, withdrawals, and tax treatment "
            "depend on your country and can change. Learn the official rules for your jurisdiction and consider "
            "a qualified tax professional for personal questions. This coach does not calculate tax outcomes."
        ),
        "next": "Check the official tax authority's current guidance for your country; do not share tax IDs or account numbers.",
    },
    "risk": {
        "message": (
            "Risk includes both the possibility of loss and whether you can stay with a plan during a downturn. "
            "Time horizon, liquidity needs, income stability, concentration, and emotional comfort all matter. "
            "A self-reported risk label is not enough to determine an appropriate portfolio."
        ),
        "next": "Think about how you would respond to a substantial temporary decline and whether you may need the money soon.",
    },
    "stock_picking": {
        "message": (
            "Researching individual companies can be educational, but concentrated positions can lose value "
            "and past performance does not predict future results. Compare the time, diversification, costs, "
            "and risks of active stock selection with broad diversified approaches. This coach will not tell "
            "you which stock to buy or sell."
        ),
        "next": "If you research a company, review primary sources, write down risks and assumptions, and avoid investing money you need soon.",
    },
    "market_timing": {
        "message": (
            "Short-term market movements are difficult to forecast consistently. Frequent trading can add "
            "transaction costs, tax complexity, and behavioral risk. A long-term plan should account for "
            "uncertainty rather than depend on predicting the next market move."
        ),
        "next": "Consider defining a written long-term process and a cooling-off period before acting on a headline or market move.",
    },
}

KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("emergency_reserve", ("emergency", "cash reserve", "rainy day")),
    ("debt", ("debt", "loan", "credit card", "interest rate")),
    ("diversification", ("diversif", "index fund", "index funds", "etf")),
    ("account_types", ("tax", "401(k)", "401k", "ira", "roth", "account")),
    ("risk", ("risk", "loss", "downturn", "volatility")),
    ("market_timing", ("timing", "trade", "trading", "market crash")),
    ("stock_picking", ("which stock", "pick stocks", "buy", "sell", "ticker")),
    ("long_term_habits", ("regular", "compound", "long term", "long-term", "habit", "monthly")),
)

SOURCES = (
    ("SEC Investor.gov: Introduction to Investing", "https://www.investor.gov/introduction-investing"),
    ("SEC Investor.gov: Beginners' Guide to Asset Allocation, Diversification, and Rebalancing", "https://www.investor.gov/introduction-investing/investing-basics/save-and-invest/diversification"),
    ("FINRA: Investing Basics", "https://www.finra.org/investors/investing/investing-basics"),
)


def assess_readiness(context: InvestorContext) -> list[str]:
    """Return neutral learning considerations; never make a suitability determination."""
    considerations: list[str] = []
    if context.emergency_reserve_ready is False:
        considerations.append("Learn how a liquid emergency reserve may fit alongside investing.")
    if context.high_interest_debt is True:
        considerations.append("Review the cost and terms of high-interest debt as part of your financial priorities.")
    if context.time_horizon.strip():
        considerations.append("Match the amount of risk you study to when you may need the money; this is not a portfolio recommendation.")
    if context.country_or_region.strip():
        considerations.append("Use official local sources for account and tax rules, which vary by jurisdiction.")
    return considerations


def classify_topic(question: str) -> str:
    normalized = question.lower()
    for topic, keywords in KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return topic
    return "getting_started"


def coach(question: str, context: InvestorContext | None = None) -> CoachReply:
    """Run a bounded coach workflow: classify → readiness check → retrieve lesson → respond with sources."""
    context = context or InvestorContext()
    topic = classify_topic(question)
    lesson = EDUCATION[topic]
    considerations = assess_readiness(context)
    message = lesson["message"]
    if considerations:
        message += "\n\nContext to consider (not a personalized recommendation):\n" + "\n".join(
            f"- {item}" for item in considerations
        )
    return CoachReply(
        topic=topic,
        message=message,
        next_step=lesson["next"],
        sources=SOURCES,
        tools_used=("topic_router", "readiness_reflection", "education_retriever", "citation_attacher"),
    )
