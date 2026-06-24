"""Scraper Agent: coloca o texto público da startup no estado.

Reaproveita o scraper do Bloco 1 (Scrapling para baixar + trafilatura para limpar).
"""

from __future__ import annotations

from graph.state import StartupState
from scraping.scrapling_fetcher import fetch_html
from scraping.trafilatura_parser import extract_main_text


def scraper_node(state: StartupState) -> dict:
    """Baixa o site da startup e devolve o texto limpo no campo raw_text."""
    url = state["url"]
    html = fetch_html(url)
    text = extract_main_text(html, url=url) or ""
    return {"raw_text": text}
