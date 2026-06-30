"""Coleta multi-página: home + páginas internas relevantes, juntando o texto limpo.

Enriquece o input do Extractor: em vez de só a home (marketing), pega também
páginas como /sobre, /tecnologia, /time e blog — onde a empresa costuma
descrever a tecnologia/modelo de verdade.

É resiliente: páginas que falham ou não têm texto são puladas, sem quebrar.
"""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

from scrapling.fetchers import Fetcher

from scraping.trafilatura_parser import extract_main_text

# Pistas no link que indicam páginas ricas em contexto técnico/institucional.
RELEVANT_HINTS = (
    # institucional
    "sobre", "about", "quem-somos", "empresa", "company", "historia", "history",
    # time e contratação (também sinalizam perfil técnico do time)
    "time", "team", "carreira", "career", "vagas", "jobs", "trabalhe",
    # produto e tecnologia
    "produto", "product", "tecnologia", "technology", "tech",
    "plataforma", "platform", "solucao", "solution", "solucoes",
    "recursos", "features", "funcionalidades", "como-funciona", "how-it-works",
    # IA
    "inteligencia", "intelligence", "machine-learning",
    # prova social / conteúdo
    "casos", "cases", "clientes", "customers", "blog",
)


def _collect_links(page, base_url: str) -> list[str]:
    """Extrai links internos relevantes (mesmo domínio + pistas), sem repetir."""
    base_domain = urlparse(base_url).netloc
    relevantes: list[str] = []
    vistos: set[str] = set()

    for href in page.css("a::attr(href)"):
        full = urljoin(base_url, str(href))      # resolve links relativos
        full = full.split("#")[0].rstrip("/")     # remove âncora e barra final
        if not full or full in vistos:
            continue
        if urlparse(full).netloc != base_domain:  # só o mesmo site
            continue
        if any(hint in full.lower() for hint in RELEVANT_HINTS):
            vistos.add(full)
            relevantes.append(full)

    return relevantes


def collect_site_text(base_url: str, max_pages: int = 5, timeout: int = 30) -> str:
    """Coleta o texto limpo da home + páginas internas relevantes, concatenado.

    Cada trecho vem marcado com a fonte (URL). Devolve "" se nem a home carregar.
    """
    try:
        home = Fetcher.get(base_url, timeout=timeout)
    except Exception:  # noqa: BLE001 — sem home, não há o que coletar
        return ""

    urls = [base_url] + _collect_links(home, base_url)
    urls = urls[:max_pages]

    partes: list[str] = []
    for url in urls:
        try:
            page = home if url == base_url else Fetcher.get(url, timeout=timeout)
            texto = extract_main_text(str(page.html_content), url=url)
        except Exception:  # noqa: BLE001 — página problemática é pulada
            texto = None
        if texto:
            partes.append(f"# Fonte: {url}\n{texto}")

    return "\n\n".join(partes)
