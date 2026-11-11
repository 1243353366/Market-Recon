"""Educational investing coach with a bounded, deterministic agent workflow.

This coach teaches general principles. It does not recommend securities or allocations,
provide tax/legal advice, or place trades.
"""

from .agent import CoachReply, InvestorContext, coach

__all__ = ["CoachReply", "InvestorContext", "coach"]
