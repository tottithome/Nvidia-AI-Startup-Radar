"""Interface web (Streamlit) do NVIDIA Startup AI Radar.

Escolha uma startup do catálogo (ou digite manualmente), rode o grafo completo e veja
classificação, perfil, checklist com evidências, correlações NVIDIA e o briefing
executivo. Análises já feitas podem ser CARREGADAS do banco (sem rodar LLM de novo).

Rodar com:
    uv run streamlit run frontend/app.py
"""

from __future__ import annotations

import streamlit as st

from db.catalog import get_catalog
from db.repository import get_latest_analysis, save_analysis
from db.session import init_db
from graph.pipeline import build_graph

st.set_page_config(page_title="NVIDIA Startup AI Radar", page_icon="🟢")
st.title("NVIDIA Startup AI Radar")
st.caption("Classifica a maturidade em IA de uma startup e recomenda tecnologias NVIDIA.")

# Garante a tabela de análises (idempotente). Se o banco estiver fora, o catálogo cai
# para a seed e apenas não salvamos/carregamos (o app segue funcionando).
_banco_ok = True
try:
    init_db()
except Exception:  # noqa: BLE001
    _banco_ok = False
    st.info("Banco indisponível: catálogo limitado à seed; análises não serão salvas.")

# --- Seleção da startup: catálogo ou entrada manual ---
catalogo = get_catalog()
MANUAL = "— digitar manualmente —"


def _rotulo(c: dict) -> str:
    if c["analisada"] and c["level"] is not None:
        return f"{c['startup_name']}  ✓ nível {c['level']}"
    if c["analisada"]:
        return f"{c['startup_name']}  ✓ analisada"
    return c["startup_name"]


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
tem_salva = bool(item and item["analisada"])
carregar = col2.button("Carregar análise salva", disabled=not tem_salva)

# --- Ação: rodar o grafo ou carregar do banco; guarda no estado da sessão ---
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
                except Exception:  # noqa: BLE001 — persistência é opcional
                    pass
        st.session_state["resultado"] = final

# --- Renderização (só mostra se o resultado é da startup selecionada) ---
resultado = st.session_state.get("resultado")
if resultado and resultado.get("startup_name") == nome:
    st.divider()

    nivel = resultado.get("level")
    if nivel is None:
        st.subheader(f"Classificação: {resultado.get('level_name') or 'Não classificado'}")
    else:
        st.subheader(f"Classificação: nível {nivel} — {resultado.get('level_name')}")
    if resultado.get("rationale"):
        st.write(resultado["rationale"])

    estruturado = resultado.get("structured") or {}
    if estruturado:
        with st.expander("Perfil extraído da startup"):
            st.json(estruturado)

    checklist = resultado.get("checklist") or []
    if checklist:
        with st.expander("Checklist de maturidade (com evidências)"):
            for i in checklist:
                st.markdown(f"**{i.get('pergunta')}. {i.get('resposta')}** — {i.get('evidencia')}")

    contexto = resultado.get("nvidia_context") or []
    if contexto:
        with st.expander("Tecnologias NVIDIA mais próximas do perfil (cosseno)"):
            for c in contexto:
                st.write(f"`{c.get('score'):.3f}` — **{c.get('technology')}** — {c.get('source_url')}")

    st.divider()
    st.markdown(resultado.get("briefing") or "_(briefing vazio — possível instabilidade do LLM)_")
