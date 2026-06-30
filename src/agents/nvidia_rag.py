"""NVIDIA RAG Agent: busca na base NVIDIA as tecnologias relevantes ao perfil da startup.

Monta uma query a partir dos dados estruturados da startup e recupera (via Qdrant,
do Bloco 2) os trechos de tecnologias NVIDIA mais próximos em significado.
"""

from __future__ import annotations

from graph.state import StartupState
from rag.retrieval import search
from rag.vector_store import get_client


def _build_query(state: StartupState) -> str:
    """Achata o perfil da startup num texto de busca."""
    structured = state.get("structured", {})
    parts = [
        state.get("startup_name", ""),
        str(structured.get("setor", "")),
        str(structured.get("produto", "")),
        str(structured.get("usa_ia", "")),
    ]
    tecnologias = structured.get("tecnologias_citadas", [])
    if isinstance(tecnologias, list):
        parts.append(" ".join(str(t) for t in tecnologias))
    # Ignora campos vazios ou marcados como "inconclusivo" (só atrapalhariam a busca).
    return " ".join(p for p in parts if p and p != "inconclusivo").strip()


def nvidia_rag_node(state: StartupState) -> dict:
    """Monta a busca a partir do perfil e recupera os trechos NVIDIA relevantes."""
    query = _build_query(state) or state.get("startup_name", "")
    client = get_client()
    chunks = search(client, query, limit=5)
    return {"nvidia_context": chunks}
