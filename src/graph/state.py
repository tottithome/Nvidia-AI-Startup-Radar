"""Estado compartilhado do grafo de classificação (LangGraph).

É o "dicionário" que passa por todos os nós. Cada agente lê o que precisa e
acrescenta o seu resultado. Os campos vão sendo preenchidos ao longo do fluxo.
"""

from __future__ import annotations

from typing import TypedDict


class StartupState(TypedDict, total=False):
    # --- entrada (fornecida no início) ---
    startup_name: str
    url: str

    # --- preenchido pelo Scraper ---
    raw_text: str

    # --- preenchido pelo Extractor ---
    structured: dict

    # --- preenchido pelo Classifier ---
    checklist: list[dict]
    level: int
    level_name: str
    rationale: str
