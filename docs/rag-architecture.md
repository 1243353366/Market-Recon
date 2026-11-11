# RAG and public-document intelligence

Market Recon's RAG layer indexes source-linked public documents for semantic and hybrid retrieval. Its first vertical is SEC EDGAR; additional collectors should normalize records into the `SourceDocument` schema before ingestion.

## Architecture

```text
Public sources / adapters
  ├─ SEC EDGAR submissions + filing documents
  ├─ Earnings, IR releases, presentations, patents, policy/regulatory feeds (planned adapters)
  └─ Local normalized JSONL imports
          ↓
Normalization + provenance metadata
          ↓
Text cleaning → overlapping chunks → configurable embeddings
          ↓
Qdrant (local persistent or hosted)
          ↓
Dense retrieval + lexical ranking → reciprocal-rank fusion
          ↓
Retrieved passages + stable source URLs / dates / filing types
          ↓
Citation-grounded answers (LLM adapter planned; retrieval results can be inspected without an LLM)
```

### Embedding options

Set `MARKET_RECON_EMBEDDING_MODEL` or pass `--model`. The default is `BAAI/bge-m3`. Other sentence-transformers-compatible models can be selected, including multilingual E5 and Jina embeddings. Verify each model's license, supported languages, vector dimensions, and usage requirements before deployment. `Instructor-xl` may require model-specific instruction formatting and should use a dedicated adapter before production use.

### Storage and retrieval

- Qdrant is the implemented vector store and supports local persistence or a hosted endpoint.
- Retrieval combines Qdrant dense results with a lightweight lexical pass and reciprocal-rank fusion.
- Metadata filters currently support exact values and lists, for example `ticker` and `document_type`.
- The lexical pass is a simple prototype, not a production BM25 engine. For larger corpora, replace it with Qdrant sparse vectors or a dedicated BM25/search service, and add a cross-encoder reranker.
- Weaviate, Milvus, and Chroma can be added behind the same knowledge-base interface; they are architecture alternatives, not active integrations yet.

## Quick start

Install RAG dependencies:

```bash
pip install -e '.[rag]'
```

Set a descriptive SEC contact User-Agent (SEC fair-access guidance requires identifying contact information):

```bash
export SEC_USER_AGENT='MarketRecon research contact@example.org'
```

Index recent SEC filings for a ticker. The embedding model downloads on first use; expect significant storage and memory requirements for large models:

```bash
python -m market_recon.rag.cli ingest-sec --ticker NVDA --forms 10-K 10-Q 8-K --limit 10
```

Search the indexed filings:

```bash
python -m market_recon.rag.cli search 'export restrictions and AI accelerators' --ticker NVDA --limit 5
```

Use a hosted Qdrant instance by setting `QDRANT_URL` and `QDRANT_API_KEY`; otherwise the index persists locally under `data/qdrant`.

## Import other public sources

Collectors for transcripts, press releases, investor presentations, FDA/patent/legal/policy records, energy and shipping reports, and trade publications are not included yet. Add a source adapter that produces JSON Lines with one object per document:

```json
{"document_id":"stable-id","title":"Document title","text":"Extracted text","source_name":"Publisher","source_url":"https://example.org/source","document_type":"press_release","published_at":"2026-01-01","ticker":"EXAMPLE","metadata":{"accession_number":"optional"}}
```

Then run:

```bash
python -m market_recon.rag.cli ingest-jsonl path/to/documents.jsonl
```

Use only public sources and respect site/API terms, rate limits, copyright, and robots/access policies. Store source URLs and retrieval times; do not treat derived or third-party datasets as official filings.

## SEC coverage and limitations

The SEC adapter downloads recent filing documents exposed by the submissions endpoint and indexes their text with filing metadata. It is a starter collector, not a complete EDGAR mirror: amendments, older paginated submissions, exhibits, XBRL normalization, retry/backoff, and filing-specific parsing need further work. Form availability varies. A 13F reports holdings on a reporting date and is not real-time; 13F holdings are not equivalent to insider trades. Validate all findings against the linked filing.

## Query planning and structured filters

For questions like “semiconductor companies mentioning export restrictions and AI accelerators during the last four quarters,” retrieval should combine semantic query text with structured filters for sector/industry, publication date, and document type. This starter has ticker and document-type filters; sector enrichment and date-range filters are next steps. For questions that require numeric constraints—such as insider purchases over $500,000 and FFO growth—use normalized transaction/fundamental tables and a deterministic query engine, then use RAG to explain evidence. Semantic similarity alone cannot reliably perform arithmetic or guarantee complete screening results.

## Citation and answer policy

Search results are returned as excerpts with source title, filing type, publication date, and direct URL. A future generation layer must cite each factual claim to retrieved passages, distinguish source facts from model inference, state when evidence is missing or conflicting, and never fabricate a citation. This code currently provides retrieval with citations, not generated investment recommendations.

## Roadmap

1. Production-grade SEC pagination, retries, rate limiting, and accession-level deduplication.
2. Reusable adapters for earnings transcripts, IR releases, and public agency feeds.
3. True BM25/sparse retrieval and cross-encoder reranking.
4. Date/sector/company filters, query decomposition, and source-aware citation validation.
5. Entity resolution and a provenance-preserving company/people/filing graph.
6. Deterministic insider-cluster and 13F change analysis from normalized records.
7. Optional provider adapters for hosted and local LLMs, with citations and structured output validation.

## Point identifiers

Qdrant accepts unsigned 64-bit integers or UUIDs as point IDs. `chunking.chunk_point_id()` derives a
deterministic UUIDv5 from each chunk's content key (`document_id:index:text-prefix`), so re-ingesting the
same document overwrites the same points instead of accumulating duplicates. The raw SHA-256 digest of the
same key is retained as `payload["content_hash"]` for change detection, and `QdrantKnowledgeBase.upsert`
rejects any ID that does not parse as a UUID before calling Qdrant.

`QdrantKnowledgeBase` still does not verify that an existing collection was built with the configured
embedding model. Writing to a collection with a different model but the same vector dimension will succeed
and silently degrade retrieval; record the model and dimension in collection metadata and refuse mismatched
writes before relying on retrieval quality.
