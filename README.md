## Reproducible SEC filing change workflow

Added an end-to-end command sequence implementing **10-K/10-Q → parse → chunk → index → compare → explain → cite**. Section chunks are indexed in Qdrant with filing provenance; parsed versions are archived in SQLite; the comparison command emits categorized candidate changes and both source URLs. See [docs/sec-filing-workflow.md](docs/sec-filing-workflow.md).
