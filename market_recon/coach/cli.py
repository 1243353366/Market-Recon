from __future__ import annotations

import argparse

from .agent import InvestorContext, coach


def main() -> None:
    parser = argparse.ArgumentParser(description="Market Recon educational investing coach")
    parser.add_argument("question", nargs="+", help="A general investing education question")
    parser.add_argument("--horizon", default="", help="Optional broad time horizon; do not provide account details")
    parser.add_argument("--region", default="", help="Optional country/region for directing you to official rules")
    parser.add_argument("--reserve-ready", choices=("yes", "no", "unsure"), default="unsure")
    parser.add_argument("--high-interest-debt", choices=("yes", "no", "unsure"), default="unsure")
    args = parser.parse_args()

    context = InvestorContext(
        time_horizon=args.horizon,
        country_or_region=args.region,
        emergency_reserve_ready={"yes": True, "no": False, "unsure": None}[args.reserve_ready],
        high_interest_debt={"yes": True, "no": False, "unsure": None}[args.high_interest_debt],
    )
    reply = coach(" ".join(args.question), context)
    print(f"Topic: {reply.topic}\n\n{reply.message}\n\nNext step: {reply.next_step}\n\nSources:")
    for title, url in reply.sources:
        print(f"- {title}: {url}")
    print("\nThis educational tool does not provide investment, tax, or legal advice.")


if __name__ == "__main__":
    main()
