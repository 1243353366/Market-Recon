# Market Recon

Market Recon is an open-source educational research toolkit for public-market information. It is not investment advice or a trading signal platform.

## Areas
- Public-document RAG prototype for SEC filings, Qdrant, and citations: [RAG architecture](docs/rag-architecture.md)
- Educational investing coach: [coach documentation](docs/investing-coach.md)
- Curated investor research catalog: [investor research](docs/investor-research.md)
- AI coding reliability benchmark: [benchmark overview](benchmark/README.md)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[rag]'
```

Run the research CLI:

```bash
python -m market_recon.cli --symbol AAPL --period 180d --report
```

Run the Streamlit app:

```bash
streamlit run dashboard/app.py
```

Run tests from the repository root (install pytest separately if needed):

```bash
python -m pytest
```

## Scope and limitations

The application is an early prototype. Price and investor examples are not authoritative live fundamentals. Verify public data at its original source. SEC ingestion and hybrid retrieval have known MVP limitations described in the RAG documentation. The coach provides general education only. The benchmark fixtures are intentionally small and are not validation of an AI system's overall reliability.

## License

MIT; see [LICENSE](LICENSE).
