"""Classifier Agent: classifica a maturidade AI-native da startup (via LLM)."""

from __future__ import annotations

import json

from agents.llm import ask_llm, parse_json
from graph.state import StartupState

SYSTEM_PROMPT = """Você é um analista que classifica a maturidade em IA de startups.

NÍVEIS (escolha exatamente um):
3 = AI-native — produz: modelo próprio, fine-tuning, pipeline de treino, dados proprietários. IA é o núcleo.
2 = AI-enabled — consome com profundidade: integra APIs de IA com workflow próprio e diferenciação real.
1 = AI-wrapper — consome superficialmente: interface sobre uma API de terceiro, sem dados ou diferenciação.
0 = Non-AI — IA ausente ou apenas cosmética.

CHECKLIST (responda as 6, cada uma com "resposta" = sim/não/inconclusivo e "evidencia"):
1. Tem evidência de modelo próprio ou fine-tuning?
2. Há perfis técnicos de IA no time (ML Engineer, MLOps, AI Researcher)?
3. A stack técnica é identificável além de "usamos IA"?
4. Há menção a dados proprietários ou datasets exclusivos?
5. O produto seria substituível por um GPT wrapper genérico?
6. Há presença de VC ou funding relevante?

Use "inconclusivo" quando o dado não estiver disponível. Classifique com o que tem.

Responda APENAS com um objeto JSON válido neste formato:
{
  "checklist": [
    {"pergunta": 1, "resposta": "sim/não/inconclusivo", "evidencia": "..."}
  ],
  "level": 0,
  "level_name": "Non-AI/AI-wrapper/AI-enabled/AI-native",
  "rationale": "justificativa curta do nível escolhido"
}"""


def classifier_node(state: StartupState) -> dict:
    """Lê os dados da startup, responde o checklist e atribui o nível."""
    structured = state.get("structured", {})
    raw_text = state.get("raw_text", "")

    user_prompt = (
        f"Dados estruturados da startup:\n"
        f"{json.dumps(structured, ensure_ascii=False, indent=2)}\n\n"
        f"Trecho do site (apoio):\n{raw_text[:2000]}"
    )
    answer = ask_llm(SYSTEM_PROMPT, user_prompt, max_tokens=1000)
    result = parse_json(answer)

    return {
        "checklist": result.get("checklist", []),
        "level": result.get("level"),
        "level_name": result.get("level_name"),
        "rationale": result.get("rationale"),
    }
