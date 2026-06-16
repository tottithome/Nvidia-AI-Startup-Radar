"""Busca o HTML bruto de uma URL usando o Scrapling.

O Scrapling cuida do fetch + parsing + bypass de anti-bot. Aqui usamos o modo
HTTP simples (`Fetcher`), que não precisa de navegador. Modos mais pesados
(stealth/dinâmico) ficam para quando algum site exigir.
"""

from __future__ import annotations

from scrapling.fetchers import Fetcher

DEFAULT_TIMEOUT = 30


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Baixa a página e devolve o HTML bruto como string.

    Levanta RuntimeError se o status HTTP não for 2xx (ex.: 404, 403, 500).
    """
    page = Fetcher.get(url, timeout=timeout)
    if not 200 <= page.status < 300:
        raise RuntimeError(f"Falha ao buscar {url}: status HTTP {page.status}")
    return str(page.html_content)
