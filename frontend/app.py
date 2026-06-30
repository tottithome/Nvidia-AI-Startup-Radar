"""Interface web (Streamlit) do NVIDIA Startup AI Radar.

Coleta nome + URL de uma startup, roda o grafo completo e mostra a classificação,
as correlações de cosseno com a base NVIDIA e o briefing executivo.

Rodar com:
    uv run streamlit run frontend/app.py
"""

from __future__ import annotations

import streamlit as st

from graph.pipeline import build_graph

st.set_page_config(page_title="NVIDIA Startup AI Radar", page_icon="🟢")

st.title("NVIDIA Startup AI Radar")
st.caption(
    "Classifica a maturidade em IA de uma startup e recomenda tecnologias NVIDIA."
)

nome = st.text_input("Nome da startup", placeholder="Ex.: Hand Talk")
url = st.text_input("URL do site oficial", placeholder="https://www.exemplo.com.br")

if st.button("Analisar", type="primary"):
    if not nome or not url:
        st.warning("Preencha o nome e a URL da startup.")
    else:
        with st.spinner("Rodando o radar (pode levar ~30s)..."):
            grafo = build_graph()
            final = grafo.invoke({"startup_name": nome, "url": url})

        # Classificação
        st.subheader(f"Classificação: nível {final.get('level')} — {final.get('level_name')}")

        # Correlações de cosseno (escondidas num expander)
        with st.expander("Tecnologias NVIDIA mais próximas do perfil (cosseno)"):
            for c in final.get("nvidia_context", []):
                st.write(
                    f"`{c.get('score'):.3f}` — **{c.get('technology')}** — {c.get('source_url')}"
                )

        # Briefing executivo (markdown renderizado)
        st.markdown("---")
        st.markdown(final.get("briefing") or "_(briefing vazio — possível instabilidade do LLM)_")
