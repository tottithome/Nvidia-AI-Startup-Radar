"""Scraper Agent: coloca o texto público da startup no estado.

Usa o coletor multi-página (home + páginas internas relevantes), do enriquecimento
da coleta — assim o Extractor e o Classifier recebem um texto mais rico.
"""

from __future__ import annotations

from graph.state import StartupState
from scraping.site_collector import collect_site_text

MIN_CHARS_UTEIS = 1000  # abaixo disso, a coleta é considerada fraca


def scraper_node(state: StartupState) -> dict:
    """Coleta o texto da startup (multi-página) e devolve no campo raw_text.

    Se a coleta vier fraca (pouco texto, típico de site SPA/JS), preenche um
    aviso em 'scrape_aviso' para o resultado deixar claro que a análise ficou
    limitada pela falta de conteúdo.
    """
    url = state["url"]
    texto = collect_site_text(url)

    aviso = ""
    if len(texto) < MIN_CHARS_UTEIS:
        aviso = (
            f"Coleta fraca: apenas {len(texto)} caracteres extraídos de {url}. "
            "O site pode ser renderizado por JavaScript (SPA); a análise pode estar limitada."
        )

    return {"raw_text": texto, "scrape_aviso": aviso}
