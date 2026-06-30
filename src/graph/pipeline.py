"""Grafo LangGraph que orquestra os agentes da pipeline.

Fluxo: START → scraper → extractor → classifier → [roteamento] → ... → briefing → END.
Depois do classifier o caminho deixa de ser fixo: startups Non-AI (nível 0) pulam o
RAG e o recommender e vão direto ao briefing — é o primeiro ponto realmente agêntico
do grafo. As demais seguem o caminho completo (nvidia_rag → recommender → briefing).
O estado (StartupState) vai sendo preenchido por cada nó ao longo do caminho.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.briefing import briefing_node
from agents.classifier import classifier_node
from agents.extractor import extractor_node
from agents.nvidia_rag import nvidia_rag_node
from agents.recommender import recommender_node
from agents.scraper import scraper_node
from graph.state import StartupState


def route_after_classifier(state: StartupState) -> str:
    """Decide o caminho depois da classificação (1ª aresta condicional do grafo).

    Non-AI (nível 0): IA ausente ou só cosmética — não há stack NVIDIA a recomendar,
    então pula o RAG e o recommender e vai direto ao briefing. Qualquer outro nível
    (1 a 3) segue o caminho completo.

    Aceita o nível como número (0) ou texto ("0"), pois o LLM pode devolver qualquer
    um dos dois. Na dúvida (nível ausente/inesperado), segue o caminho completo.
    """
    if str(state.get("level")) == "0":
        return "briefing"
    return "nvidia_rag"


def build_graph():
    """Monta e compila o grafo dos 3 agentes."""
    builder = StateGraph(StartupState)

    # Registra os nós (cada um é uma função que recebe e atualiza o estado).
    builder.add_node("scraper", scraper_node)
    builder.add_node("extractor", extractor_node)
    builder.add_node("classifier", classifier_node)
    builder.add_node("nvidia_rag", nvidia_rag_node)
    builder.add_node("recommender", recommender_node)
    builder.add_node("briefing", briefing_node)

    # Liga os nós em sequência.
    builder.add_edge(START, "scraper")
    builder.add_edge("scraper", "extractor")
    builder.add_edge("extractor", "classifier")

    # Aresta condicional: depois de classificar, o caminho depende do nível.
    # Non-AI (0) → briefing direto; demais → caminho completo (RAG → recommender).
    builder.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {"nvidia_rag": "nvidia_rag", "briefing": "briefing"},
    )

    builder.add_edge("nvidia_rag", "recommender")
    builder.add_edge("recommender", "briefing")
    builder.add_edge("briefing", END)

    return builder.compile()
