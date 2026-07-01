"""NVIDIA RAG Agent: busca na base NVIDIA as tecnologias relevantes ao perfil da startup.

Monta uma query a partir dos dados estruturados da startup e recupera (via Qdrant,
do Bloco 2) os trechos de tecnologias NVIDIA mais próximos em significado.
"""

from __future__ import annotations

from graph.state import StartupState
from rag.retrieval import search
from rag.vector_store import get_client


def _clean(value) -> str:
    """Normaliza um campo do 'structured' em texto; descarta vazio/'inconclusivo'."""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    value = str(value or "").strip()
    return "" if value.lower() in ("", "inconclusivo", "none") else value


def _build_query(state: StartupState) -> str:
    """Monta a query de busca a partir do perfil TÉCNICO da startup.

    Em vez de achatar tudo (inclusive o nome, que é ruído e não casa com os docs
    NVIDIA), descreve em linguagem natural O QUE a empresa faz e COMO usa IA — que
    é o que bate com os casos de uso das tecnologias NVIDIA (voz, dados tabulares,
    serving, saúde...). Produto e uso de IA vêm primeiro por concentrarem o sinal.
    """
    structured = state.get("structured", {})
    produto = _clean(structured.get("produto"))
    usa_ia = _clean(structured.get("usa_ia"))
    setor = _clean(structured.get("setor"))
    techs = _clean(structured.get("tecnologias_citadas"))
    sinais = _clean(structured.get("sinais_time_tecnico"))

    partes = []
    if produto:
        partes.append(f"Produto: {produto}.")
    if usa_ia:
        partes.append(f"Uso de IA: {usa_ia}.")
    if setor:
        partes.append(f"Setor: {setor}.")
    if techs:
        partes.append(f"Tecnologias usadas: {techs}.")
    if sinais:
        partes.append(f"Perfil técnico do time: {sinais}.")
    return " ".join(partes).strip()


def nvidia_rag_node(state: StartupState) -> dict:
    """Monta a busca a partir do perfil e recupera os trechos NVIDIA relevantes.

    Busca vetorial por cosseno (top-5). O reranker (rag/reranker.py) existe como
    opção, mas está fora do fluxo: com a query por perfil técnico, o cosseno puro
    ficou mais preciso e sem o custo do modelo de rerank.
    """
    query = _build_query(state) or state.get("startup_name", "")
    client = get_client()
    chunks = search(client, query, limit=5)
    return {"nvidia_context": chunks}
