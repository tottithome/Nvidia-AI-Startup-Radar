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

# As 16 tecnologias NVIDIA (nome, URL oficial). URLs vindas do CLAUDE.md/TAP.
SOURCES = [
    # --- mínimo funcional original ---
    ("NVIDIA NIM", "https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/"),
    ("NVIDIA NeMo", "https://www.nvidia.com/en-us/ai-data-science/products/nemo/"),
    ("NVIDIA Inception", "https://www.nvidia.com/en-us/startups/"),
    # --- demais tecnologias (P2: cobertura completa) ---
    ("NeMo Guardrails", "https://github.com/NVIDIA/NeMo-Guardrails"),
    ("NVIDIA Triton Inference Server", "https://developer.nvidia.com/triton-inference-server"),
    ("TensorRT-LLM", "https://github.com/NVIDIA/TensorRT-LLM"),
    ("NVIDIA RAPIDS", "https://rapids.ai/"),
    ("cuDF", "https://docs.rapids.ai/api/cudf/stable/"),
    ("cuML", "https://docs.rapids.ai/api/cuml/stable/"),
    ("CUDA", "https://developer.nvidia.com/cuda-toolkit"),
    ("NVIDIA Riva", "https://developer.nvidia.com/riva"),
    ("NVIDIA Omniverse", "https://www.nvidia.com/en-us/omniverse/"),
    ("NVIDIA Isaac", "https://developer.nvidia.com/isaac"),
    ("NVIDIA Clara", "https://www.nvidia.com/en-us/clara/"),
    ("NVIDIA Morpheus", "https://developer.nvidia.com/morpheus-cybersecurity"),
    ("NVIDIA AI Enterprise", "https://www.nvidia.com/en-us/data-center/products/ai-enterprise/"),
]

def main() -> int:
    client = get_client()

    # Zera a coleção para um estado limpo (evita duplicatas ao re-rodar).
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    ensure_collection(client)

    total = 0
    fracas: list[tuple[str, str]] = []  # (tecnologia, motivo) das que não renderam
    for technology, url in SOURCES:
        print(f"Ingerindo {technology}...")
        try:
            n = ingest_document(client, technology, url)
        except Exception as e:  # noqa: BLE001 — uma URL ruim não pode abortar o lote
            print(f"  [ERRO] {type(e).__name__}: {e}")
            fracas.append((technology, "erro no fetch"))
            continue
        print(f"  {n} chunks inseridos")
        total += n
        if n == 0:
            fracas.append((technology, "0 chunks"))

    print(f"\n[OK] Ingestao concluida: {total} chunks de {len(SOURCES)} tecnologias.")
    if fracas:
        print("\n[ATENCAO] Tecnologias sem conteudo aproveitavel (revisar a fonte):")
        for tech, motivo in fracas:
            print(f"  - {tech} ({motivo})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
