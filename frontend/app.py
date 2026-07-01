"""Interface web (Streamlit) do NVIDIA Startup AI Radar.

Duas abas:
- Analisar startup (MICRO): escolhe do catálogo ou digita, roda o grafo, mostra
  classificação, perfil, checklist, correlações NVIDIA e briefing. Carrega análises
  salvas sem rodar LLM.
- Radar de Mercado (MACRO / diferencial): agrega as análises salvas num panorama de
  mercado com leitura estratégica para o gerente do Inception.

Rodar com:
    uv run streamlit run frontend/app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from db.catalog import get_catalog
from db.market import market_briefing, market_radar
from db.repository import get_latest_analysis, save_analysis
from db.session import init_db
from graph.pipeline import build_graph

st.set_page_config(page_title="NVIDIA Startup AI Radar", page_icon="🟢", layout="wide")
st.title("NVIDIA Startup AI Radar")
st.caption("Classifica a maturidade em IA de startups brasileiras e recomenda tecnologias NVIDIA.")

_banco_ok = True
try:
    init_db()
except Exception:  # noqa: BLE001
    _banco_ok = False
    st.info("Banco indisponível: catálogo limitado à seed; análises não serão salvas.")

tab_micro, tab_macro = st.tabs(["🔍 Analisar startup", "📊 Radar de Mercado"])


# ----------------------------------------------------------------------------
# MICRO — análise de uma startup
# ----------------------------------------------------------------------------
def _render_analise(resultado: dict) -> None:
    nivel = resultado.get("level")
    if nivel is None:
        st.subheader(f"Classificação: {resultado.get('level_name') or 'Não classificado'}")
    else:
        st.subheader(f"Classificação: nível {nivel} — {resultado.get('level_name')}")
    if resultado.get("rationale"):
        st.write(resultado["rationale"])

    if resultado.get("structured"):
        with st.expander("Perfil extraído da startup"):
            st.json(resultado["structured"])

    if resultado.get("checklist"):
        with st.expander("Checklist de maturidade (com evidências)"):
            for i in resultado["checklist"]:
                st.markdown(f"**{i.get('pergunta')}. {i.get('resposta')}** — {i.get('evidencia')}")

    if resultado.get("nvidia_context"):
        with st.expander("Tecnologias NVIDIA mais próximas do perfil (cosseno)"):
            for c in resultado["nvidia_context"]:
                st.write(f"`{c.get('score'):.3f}` — **{c.get('technology')}** — {c.get('source_url')}")

    st.divider()
    st.markdown(resultado.get("briefing") or "_(briefing vazio — possível instabilidade do LLM)_")


with tab_micro:
    catalogo = get_catalog()
    MANUAL = "— digitar manualmente —"

    def _rotulo(c: dict) -> str:
        if c["analisada"] and c["level"] is not None:
            return f"{c['startup_name']}  ✓ nível {c['level']}"
        return f"{c['startup_name']}  ✓ analisada" if c["analisada"] else c["startup_name"]

    rotulos = [MANUAL] + [_rotulo(c) for c in catalogo]
    escolha = st.selectbox("Startup", rotulos)

    if escolha == MANUAL:
        nome = st.text_input("Nome da startup", placeholder="Ex.: Hand Talk")
        url = st.text_input("URL do site oficial", placeholder="https://www.exemplo.com.br")
        item = None
    else:
        item = catalogo[rotulos.index(escolha) - 1]
        nome, url = item["startup_name"], item["url"]
        st.caption(f"**{nome}** — {url}")

    col1, col2 = st.columns(2)
    analisar = col1.button("Analisar", type="primary")
    carregar = col2.button("Carregar análise salva", disabled=not bool(item and item["analisada"]))

    if carregar and nome:
        salva = get_latest_analysis(nome)
        if salva:
            st.session_state["resultado"] = salva
        else:
            st.warning("Nenhuma análise salva encontrada para esta startup.")
    elif analisar:
        if not nome or not url:
            st.warning("Escolha uma startup do catálogo ou preencha nome e URL.")
        else:
            with st.spinner("Rodando o radar (pode levar ~30s)..."):
                final = build_graph().invoke({"startup_name": nome, "url": url})
                if _banco_ok:
                    try:
                        save_analysis(final)
                    except Exception:  # noqa: BLE001
                        pass
            st.session_state["resultado"] = final

    resultado = st.session_state.get("resultado")
    if resultado and resultado.get("startup_name") == nome:
        st.divider()
        _render_analise(resultado)


# ----------------------------------------------------------------------------
# MACRO — Radar de Mercado (diferencial)
# ----------------------------------------------------------------------------
with tab_macro:
    st.subheader("Radar de Mercado")
    st.caption("Panorama agregado das startups analisadas — leitura Macro para o Inception.")

    radar = market_radar()
    if radar["total"] == 0:
        st.info("Nenhuma análise salva ainda. Analise startups na outra aba (ou rode "
                "`uv run python scripts/analyze_catalog.py`).")
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.metric("Startups analisadas", radar["total"])
            st.write("**Distribuição de maturidade**")
            dist_df = pd.DataFrame(
                list(radar["distribuicao"].items()), columns=["Nível", "Startups"]
            ).set_index("Nível")
            st.bar_chart(dist_df)
        with c2:
            st.write("**Tecnologias NVIDIA mais demandadas**")
            for tech, n in radar["top_tecnologias"]:
                st.write(f"- **{tech}** — {n} startups")

        st.write("**Prioridade de abordagem** (mais madura primeiro)")
        for p in radar["prioridade"]:
            nivel = p["level"] if p["level"] is not None else "—"
            st.write(f"- `nível {nivel}` — {p['startup']}")

        st.divider()
        if st.button("Gerar leitura estratégica de mercado (1 chamada LLM)"):
            with st.spinner("Gerando leitura estratégica..."):
                st.session_state["market_briefing"] = market_briefing(radar)
        if st.session_state.get("market_briefing"):
            st.markdown(st.session_state["market_briefing"])
