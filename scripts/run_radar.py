"""Roda o radar completo para uma startup: scraping → classificação → recomendação → briefing.

É o MVP de ponta a ponta (Bloco 4).

Uso:
    uv run python scripts/run_radar.py "Nome da Startup" https://www.site.com.br
"""

from __future__ import annotations

import sys

from graph.pipeline import build_graph


def main() -> int:
    if len(sys.argv) != 3:
        print('Uso: uv run python scripts/run_radar.py "Nome da Startup" <url>')
        return 1

    startup_name, url = sys.argv[1], sys.argv[2]

    graph = build_graph()
    print(f"Rodando o radar para '{startup_name}' ({url})...\n")
    final = graph.invoke({"startup_name": startup_name, "url": url})

    aviso = final.get("scrape_aviso")
    if aviso:
        print(f"[AVISO] {aviso}\n")

    print(f"Classificacao: nivel {final.get('level')} - {final.get('level_name')}\n")

    print("Tecnologias NVIDIA mais proximas do perfil (similaridade de cosseno, 0 a 1):")
    for c in final.get("nvidia_context", []):
        print(f"  {c.get('score'):.3f}  [{c.get('technology')}]  {c.get('source_url')}")
    print()

    print("=" * 60)
    print("BRIEFING EXECUTIVO")
    print("=" * 60)
    print(final.get("briefing") or "(briefing vazio - possivel instabilidade do LLM)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
