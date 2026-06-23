"""Ingestão: pega uma página, quebra em chunks, vetoriza e guarda no Qdrant."""

from __future__ import annotations

from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from rag.chunking import chunk_text
from rag.embeddings import embed_texts
from rag.vector_store import COLLECTION_NAME
from scraping.scrapling_fetcher import fetch_html
from scraping.trafilatura_parser import extract_main_text


def ingest_document(client: QdrantClient, technology: str, url: str) -> int:
    """Coleta uma página, processa e guarda os chunks no Qdrant.

    Devolve quantos chunks foram inseridos.
    """
    html = fetch_html(url)
    text = extract_main_text(html, url=url)
    if not text:
        return 0

    chunks = chunk_text(text)
    vectors = embed_texts(chunks)

    points = [
        PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "technology": technology,
                "source_url": url,
                "text": chunk,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)
