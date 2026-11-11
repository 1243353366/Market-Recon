from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from qdrant_client import QdrantClient, models

from .embeddings import Embedder
from .models import DocumentChunk, SearchHit


class QdrantKnowledgeBase:
    """Qdrant-backed vector store with a lightweight BM25-like lexical fusion pass."""

    def __init__(
        self,
        embedder: Embedder,
        collection_name: str = "market_recon_documents",
        path: str = "data/qdrant",
        url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.embedder = embedder
        self.collection_name = collection_name
        self.client = QdrantClient(url=url, api_key=api_key) if url else QdrantClient(path=path)
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedder.dimension, distance=models.Distance.COSINE),
            )

    def upsert(self, chunks: list[DocumentChunk], batch_size: int = 64) -> int:
        count = 0
        for offset in range(0, len(chunks), batch_size):
            batch = chunks[offset : offset + batch_size]
            vectors = self.embedder.embed_documents([item.text for item in batch])
            points = [
                models.PointStruct(
                    id=item.chunk_id,
                    vector=vector,
                    payload={**item.metadata, "chunk_id": item.chunk_id, "document_id": item.document_id,
                              "chunk_index": item.chunk_index, "text": item.text},
                )
                for item, vector in zip(batch, vectors, strict=True)
            ]
            self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
            count += len(points)
        return count

    def search(
        self,
        query: str,
        limit: int = 8,
        filters: dict[str, Any] | None = None,
        dense_candidates: int = 40,
    ) -> list[SearchHit]:
        """Fuse vector and lexical rankings with reciprocal-rank fusion; return cited chunks."""
        query_filter = _make_filter(filters or {})
        dense = self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedder.embed_query(query),
            query_filter=query_filter,
            limit=max(limit, dense_candidates),
            with_payload=True,
        ).points
        dense_rank = {str(point.id): rank for rank, point in enumerate(dense, start=1)}

        # Lexical pass is restricted to the same metadata filter and is adequate for a local MVP.
        all_points, next_offset = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )
        while next_offset is not None and len(all_points) < 10000:
            page, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                offset=next_offset,
                limit=1000,
                with_payload=True,
                with_vectors=False,
            )
            all_points.extend(page)

        terms = _terms(query)
        lexical_scores: list[tuple[str, float]] = []
        for point in all_points:
            payload = point.payload or {}
            text = str(payload.get("text", ""))
            doc_terms = _terms(text)
            if not terms or not doc_terms:
                continue
            frequencies = defaultdict(int)
            for term in doc_terms:
                frequencies[term] += 1
            score = sum((1 + (frequencies[t] > 0) * 2) * min(frequencies[t], 3) for t in terms)
            if score:
                lexical_scores.append((str(point.id), float(score)))
        lexical_scores.sort(key=lambda pair: pair[1], reverse=True)
        lexical_rank = {point_id: rank for rank, (point_id, _) in enumerate(lexical_scores[:dense_candidates], start=1)}

        by_id = {str(point.id): point for point in dense}
        by_id.update({str(point.id): point for point in all_points if str(point.id) in lexical_rank})
        rrf: dict[str, float] = defaultdict(float)
        for point_id, rank in dense_rank.items():
            rrf[point_id] += 1 / (60 + rank)
        for point_id, rank in lexical_rank.items():
            rrf[point_id] += 1 / (60 + rank)

        results: list[SearchHit] = []
        for point_id, score in sorted(rrf.items(), key=lambda item: item[1], reverse=True)[:limit]:
            point = by_id[point_id]
            payload = point.payload or {}
            results.append(SearchHit(
                chunk_id=point_id,
                document_id=str(payload.get("document_id", "")),
                text=str(payload.get("text", "")),
                score=score,
                metadata={key: value for key, value in payload.items() if key != "text"},
            ))
        return results


def _make_filter(filters: dict[str, Any]) -> models.Filter | None:
    conditions = []
    for key, value in filters.items():
        if isinstance(value, list):
            conditions.append(models.FieldCondition(key=key, match=models.MatchAny(any=value)))
        else:
            conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=value)))
    return models.Filter(must=conditions) if conditions else None


def _terms(text: str) -> list[str]:
    return [word.lower() for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9.-]{1,}", text)]
