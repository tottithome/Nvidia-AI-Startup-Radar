"""Grafo LangGraph que orquestra os agentes do Bloco 3.

Fluxo linear: START → scraper → extractor → classifier → END.
O estado (StartupState) vai sendo preenchido por cada nó ao longo do caminho.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.classifier import classifier_node
from agents.extractor import extractor_node
from agents.scraper import scraper_node
from graph.state import StartupState


def build_graph():
    """Monta e compila o grafo dos 3 agentes."""
    builder = StateGraph(StartupState)

    # Registra os nós (cada um é uma função que recebe e atualiza o estado).
    builder.add_node("scraper", scraper_node)
    builder.add_node("extractor", extractor_node)
    builder.add_node("classifier", classifier_node)

    # Liga os nós em sequência.
    builder.add_edge(START, "scraper")
    builder.add_edge("scraper", "extractor")
    builder.add_edge("extractor", "classifier")
    builder.add_edge("classifier", END)

    return builder.compile()
