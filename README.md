# Market Recon RAG

The RAG starter indexes public SEC filings and normalized JSONL documents in Qdrant and returns semantic/lexical search results with source URLs and metadata.

Install and usage instructions: [RAG architecture and quick start](docs/rag-architecture.md).

This implementation is an early prototype. It is not a comprehensive data collector, doesn't cover all source families, and doesn't produce investment advice or reliably perform numeric screens from prose. Use structured data for quantitative filters and verify conclusions against original sources.
