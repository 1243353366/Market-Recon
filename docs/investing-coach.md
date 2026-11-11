# Educational Investing Coach

Market Recon includes an early, bounded investing-education coach. It uses a deterministic agent workflow—topic routing, optional readiness reflection, retrieval of a reviewed educational response, and source attachment. It does not call an LLM, execute trades, select securities, or generate allocations.

## Run

```bash
python -m market_recon.coach.cli "How does diversification work?"
streamlit run dashboard/app.py
```

The coach page appears in Streamlit's multipage navigation. You can optionally provide broad context such as a time horizon, whether you have a cash reserve, whether high-interest debt is a concern, and a country/region for official account-rule resources. All context is optional; do not submit exact balances, account identifiers, tax IDs, or credentials.

## Agent workflow

1. `topic_router` maps the question to a general learning topic.
2. `readiness_reflection` surfaces neutral considerations from optional context; it does not determine suitability.
3. `education_retriever` selects a fixed educational response.
4. `citation_attacher` includes public investor-education sources.

The current version is intentionally deterministic and inspectable. Adding an LLM later would require strict evidence-grounded generation, citation verification, privacy review, output evaluations, and guardrails; a system prompt alone is not a sufficient safety mechanism.

## Boundaries

- General investing education, not personalized advice or a fiduciary service.
- No buy/sell/hold recommendations, ticker picks, portfolio allocations, return forecasts, or trade execution.
- No individualized tax or legal conclusions.
- Market risk remains; broad diversification does not eliminate losses.
- Tax rules vary by jurisdiction and change. Consult official sources and qualified professionals for personal questions.
- Responses are not a substitute for professional advice.

## Sources

The included lessons are general and cite SEC Investor.gov and FINRA investor education. Check current official sources and applicable rules for your location.
