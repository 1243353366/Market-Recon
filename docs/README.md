# Market Recon RAG Architecture

Market Recon is evolving from a price dashboard into a public-document research and intelligence platform. The RAG architecture and working SEC/Qdrant starter are documented in [docs/rag-architecture.md](docs/rag-architecture.md).

The current implementation supports SEC filing ingestion, local JSONL document imports, configurable sentence-transformer embeddings, Qdrant storage, hybrid dense/lexical retrieval, and citation-bearing search results. Most other listed source categories and LLM providers remain planned adapters; see the architecture doc for scope and limitations.
