"""Integracao com a API do Google Gemini para o assistente de IA do quiz.

A chamada e feita inteiramente no backend: a chave de API nunca trafega
para o navegador do usuario.
"""

import httpx

from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.questao import Questao

GEMINI_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class AssistenteIAIndisponivelError(Exception):
    """Levantada quando o assistente de IA nao esta configurado ou falha."""


def montar_prompt(questao: Questao) -> str:
    """Monta o prompt enviado ao Gemini a partir dos dados da questao."""
    alternativas = "\n".join(
        f"{letra}) {texto}"
        for letra, texto in (
            ("A", questao.alternativa_a),
            ("B", questao.alternativa_b),
            ("C", questao.alternativa_c),
            ("D", questao.alternativa_d),
            ("E", questao.alternativa_e),
        )
    )
    return (
        "Voce e um tutor ajudando um estudante de Engenharia de Computacao a "
        "se preparar para a prova do ENADE. Explique, em portugues, de forma "
        "breve e didatica (no maximo 5 frases), por que a alternativa correta "
        "esta certa e, se fizer sentido, por que as outras nao servem. Nao "
        "repita o enunciado inteiro.\n\n"
        f"Questao:\n{questao.enunciado}\n\n"
        f"Alternativas:\n{alternativas}\n\n"
        f"Alternativa correta: {questao.resposta}"
    )


async def explicar_questao(questao: Questao) -> str:
    """Pede ao Gemini uma explicacao curta sobre a questao."""
    if not GEMINI_API_KEY:
        raise AssistenteIAIndisponivelError(
            "O assistente de IA nao esta configurado neste servidor "
            "(falta GEMINI_API_KEY)."
        )

    url = f"{GEMINI_URL_BASE}/{GEMINI_MODEL}:generateContent"
    corpo = {"contents": [{"parts": [{"text": montar_prompt(questao)}]}]}

    async with httpx.AsyncClient(timeout=20) as cliente:
        try:
            resposta = await cliente.post(
                url,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },
                json=corpo,
            )
            resposta.raise_for_status()
        except httpx.HTTPError as erro:
            raise AssistenteIAIndisponivelError(
                "Nao foi possivel consultar o assistente de IA agora. "
                "Tente novamente em instantes."
            ) from erro

    dados = resposta.json()
    try:
        texto = dados["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as erro:
        raise AssistenteIAIndisponivelError(
            "O assistente de IA devolveu uma resposta inesperada."
        ) from erro

    return texto.strip()
