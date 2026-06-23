"""Ingere as documentações de tecnologias NVIDIA no Qdrant (Bloco 2).

Recria a coleção do zero e ingere as páginas oficiais de cada tecnologia.
É seguro rodar de novo: a coleção é zerada antes, evitando duplicatas.

Uso:
    uv run python scripts/ingest_nvidia.py
"""

from __future__ import annotations

import sys

from rag.ingestion import ingest_document
from rag.vector_store import COLLECTION_NAME, ensure_collection, get_client

# Tecnologias do mínimo funcional: (nome, URL oficial)
SOURCES = [
    ("NVIDIA NIM", "https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/"),
    ("NVIDIA NeMo", "https://www.nvidia.com/en-us/ai-data-science/products/nemo/"),
    ("NVIDIA Inception", "https://www.nvidia.com/en-us/startups/"),
]

def main() -> int:
    client = get_client()

    # Zera a coleção para um estado limpo (evita duplicatas ao re-rodar).
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    ensure_collection(client)

    total = 0
    for technology, url in SOURCES:
        print(f"Ingerindo {technology}...")
        n = ingest_document(client, technology, url)
        print(f"  {n} chunks inseridos")
        total += n

    print(f"[OK] Ingestao concluida: {total} chunks no total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
