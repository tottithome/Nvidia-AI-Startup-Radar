"""Briefing Agent: gera o relatório executivo final para o gerente da NVIDIA."""

from __future__ import annotations

from agents.llm import ask_llm
from graph.state import StartupState

SYSTEM_PROMPT = (
    "Você redige um briefing executivo, em português e em markdown, para o gerente "
    "de Startups & VCs da NVIDIA Brasil (programa Inception). Tom construtivo e de "
    "apoio, linguagem objetiva. Estruture em seções: Resumo da startup; Classificação "
    "de maturidade (com a justificativa); Recomendações NVIDIA; Próxima ação sugerida. "
    "Escreva o markdown diretamente, sem envolver tudo em um bloco de código."
)


def briefing_node(state: StartupState) -> dict:
    """Sintetiza classificação + recomendações num relatório executivo."""
    checklist = state.get("checklist", [])
    checklist_txt = "\n".join(
        f"  {item.get('pergunta')}. {item.get('resposta')} - {item.get('evidencia')}"
        for item in checklist
    )

    user_prompt = (
        f"Startup: {state.get('startup_name')}\n"
        f"Maturidade: nível {state.get('level')} ({state.get('level_name')})\n"
        f"Justificativa da classificação: {state.get('rationale')}\n\n"
        f"Checklist preenchido:\n{checklist_txt}\n\n"
        f"Recomendações geradas:\n{state.get('recommendations')}\n\n"
        f"Escreva o briefing executivo."
    )

    briefing = ask_llm(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
    return {"briefing": briefing}
