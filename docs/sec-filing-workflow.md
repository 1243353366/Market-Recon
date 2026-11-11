# SEC filing workflow: 10-K/10-Q → parse → chunk → index → compare → explain → cite

A small end-to-end CLI uses the existing SEC EDGAR client, rule-based section parser, chunker, and Qdrant index. Parsed filing versions are also stored in SQLite so comparisons are repeatable and can be run separately from ingestion.

## Setup

Install optional RAG dependencies and provide an identifying SEC User-Agent:

```bash
pip install -e '.[rag]'
export SEC_USER_AGENT='MarketRecon research contact@example.org'
```

The first command downloads the configured embedding model if needed. It fetches recent 10-Ks (or 10-Qs), parses the filing into Item sections, archives parsed versions in SQLite, chunks each section with source metadata, and indexes chunks in Qdrant:

```bash
python -m market_recon.sources.filing_cli ingest --ticker NVDA --form 10-K --limit 10
```

Then compare the latest two archived versions and emit JSON with categorized changed passages and citations to both filing versions:

```bash
python -m market_recon.sources.filing_cli compare --ticker NVDA --form 10-K
```

Configuration options (`--database`, `--model`, `--qdrant-path`, `--qdrant-url`, `--qdrant-api-key`) are available on both subcommands. Secrets should be passed through environment variables, not committed. The filing archive defaults to `data/market.db`; the vector index defaults to `data/qdrant`.

## Workflow

```text
10-K / 10-Q
    ↓
SEC EDGAR fetch (original filing URL retained)
    ↓
HTML/text extraction and Item-section parsing
    ↓
Section-aware chunking with filing date, CIK, ticker, accession, URL, and section metadata
    ↓
Qdrant indexing for retrieval
    ↓
SQLite version archive for reproducible pairwise comparison
    ↓
Changed-section diff + transparent heuristic categories
    ↓
JSON explanations with before/after citations
```

The explanation states why a line was surfaced by the keyword/section heuristic; it is not an LLM-generated factual conclusion. The current detector may miss semantic changes or flag formatting/boilerplate changes. “Removed” means absent from compared parsed text, not that a risk ended. Review both linked filings. The pipeline is educational research software, not investment advice or a predictive system.
