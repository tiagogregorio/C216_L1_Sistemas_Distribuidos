"""Integracao com a API do Google Gemini para o assistente de IA do quiz.

A chamada e feita inteiramente no backend: a chave de API nunca trafega
para o navegador do usuario.
"""

import asyncio
import json
import unicodedata

import httpx

from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.questao import Questao

GEMINI_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

ASSUNTOS_CONHECIDOS = [
    "Algoritmos de Ordenacao",
    "Banco de Dados",
    "Circuitos Eletricos",
    "Compiladores",
    "Computacao em Nuvem",
    "Controle e Automacao",
    "Criptografia",
    "Engenharia de Software",
    "Estruturas de Dados",
    "Grafos",
    "Inteligencia Artificial",
    "Interacao Humano-Computador",
    "Linguagem C",
    "Linguagens Formais",
    "Matematica Discreta",
    "Padroes de Projeto",
    "Programacao Concorrente",
    "Programacao Funcional",
    "Redes de Computadores",
    "Sistemas Embarcados",
    "Sistemas Operacionais",
]

DIFICULDADES_VALIDAS = {"facil", "medio", "dificil"}
STATUS_COM_NOVA_TENTATIVA = {429, 500, 502, 503, 504}
ESPERAS_ENTRE_TENTATIVAS = (2, 5)  # segundos


class AssistenteIAIndisponivelError(Exception):
    """Levantada quando o assistente de IA nao esta configurado ou falha."""


def ia_configurada() -> bool:
    """Indica se ha uma chave do Gemini configurada (sem expor a chave)."""
    return bool(GEMINI_API_KEY)


def modelo_ia() -> str:
    return GEMINI_MODEL


def _sem_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


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


def _mensagem_para_status(status: int, corpo: str) -> str:
    """Traduz um erro HTTP do Gemini para algo que o usuario consiga agir."""
    if "API key" in corpo or status in (401, 403):
        return (
            "O Gemini recusou a chave de API (invalida ou sem permissao). "
            "Confira GEMINI_API_KEY no arquivo .env."
        )
    if status == 404:
        return (
            f"O modelo '{GEMINI_MODEL}' nao foi encontrado. "
            "Ajuste GEMINI_MODEL no arquivo .env."
        )
    if status == 429:
        return (
            "O limite de uso gratuito do Gemini foi atingido. "
            "Aguarde cerca de um minuto e tente de novo."
        )
    if status >= 500:
        return (
            "O servico do Gemini esta instavel no momento. "
            "Tente novamente em instantes."
        )
    return f"O Gemini recusou a requisicao (HTTP {status})."


def _extrair_texto(resposta: httpx.Response) -> str:
    try:
        dados = resposta.json()
        return dados["candidates"][0]["content"]["parts"][0]["text"]
    except (ValueError, KeyError, IndexError, TypeError) as erro:
        raise AssistenteIAIndisponivelError(
            "O assistente de IA devolveu uma resposta inesperada."
        ) from erro


async def _chamar_gemini(
    prompt: str, *, json_mode: bool = False, timeout: float = 60
) -> str:
    """Chama o Gemini (com novas tentativas em limite de uso/instabilidade)."""
    if not GEMINI_API_KEY:
        raise AssistenteIAIndisponivelError(
            "O assistente de IA nao esta configurado neste servidor "
            "(falta GEMINI_API_KEY)."
        )

    url = f"{GEMINI_URL_BASE}/{GEMINI_MODEL}:generateContent"
    corpo = {"contents": [{"parts": [{"text": prompt}]}]}
    if json_mode:
        corpo["generationConfig"] = {"responseMimeType": "application/json"}
    cabecalhos = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

    ultimo_erro = "Nao foi possivel consultar o assistente de IA."
    async with httpx.AsyncClient(timeout=timeout) as cliente:
        for tentativa in range(len(ESPERAS_ENTRE_TENTATIVAS) + 1):
            try:
                resposta = await cliente.post(url, headers=cabecalhos, json=corpo)
            except httpx.HTTPError:
                ultimo_erro = (
                    "Nao foi possivel conectar ao Gemini. Verifique se o "
                    "container tem acesso a internet."
                )
            else:
                if resposta.status_code == 200:
                    return _extrair_texto(resposta)
                ultimo_erro = _mensagem_para_status(resposta.status_code, resposta.text)
                if resposta.status_code not in STATUS_COM_NOVA_TENTATIVA:
                    break
            if tentativa < len(ESPERAS_ENTRE_TENTATIVAS):
                await asyncio.sleep(ESPERAS_ENTRE_TENTATIVAS[tentativa])

    raise AssistenteIAIndisponivelError(ultimo_erro)


async def explicar_questao(questao: Questao) -> str:
    """Pede ao Gemini uma explicacao curta sobre a questao."""
    texto = await _chamar_gemini(montar_prompt(questao))
    return texto.strip()


def _interpretar_classificacao(texto: str, quantidade: int) -> list[dict]:
    """Converte o JSON devolvido pelo Gemini em uma lista alinhada as questoes.

    Questoes que a IA nao classificou ficam com assunto vazio e dificuldade
    "medio" (o usuario ainda pode editar na tela de revisao).
    """
    limpo = (
        texto.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    try:
        dados = json.loads(limpo)
    except json.JSONDecodeError as erro:
        raise AssistenteIAIndisponivelError(
            "A IA devolveu uma classificacao ilegivel. Tente novamente."
        ) from erro

    if isinstance(dados, dict):  # alguns modelos embrulham a lista numa chave
        for valor in dados.values():
            if isinstance(valor, list):
                dados = valor
                break
    if not isinstance(dados, list):
        raise AssistenteIAIndisponivelError(
            "A IA devolveu uma classificacao em formato inesperado."
        )

    conhecidos = {_sem_acentos(a).lower(): a for a in ASSUNTOS_CONHECIDOS}
    resultado = [{"assunto": "", "dificuldade": "medio"} for _ in range(quantidade)]
    for posicao, item in enumerate(dados):
        if not isinstance(item, dict):
            continue
        indice = item.get("indice", posicao)
        if not isinstance(indice, int) or not 0 <= indice < quantidade:
            continue
        assunto = _sem_acentos(str(item.get("assunto", ""))).strip()[:100]
        assunto = conhecidos.get(assunto.lower(), assunto)
        dificuldade = _sem_acentos(str(item.get("dificuldade", ""))).strip().lower()
        if dificuldade not in DIFICULDADES_VALIDAS:
            dificuldade = "medio"
        resultado[indice] = {"assunto": assunto, "dificuldade": dificuldade}
    return resultado


async def classificar_lote(questoes: list[dict]) -> list[dict]:
    """Classifica assunto e dificuldade de varias questoes em UMA chamada.

    Cada item de `questoes` tem enunciado e alternativa_a..alternativa_e.
    Devolve uma lista na mesma ordem: [{"assunto": ..., "dificuldade": ...}].
    """
    if not questoes:
        return []

    blocos = []
    for i, q in enumerate(questoes):
        alternativas = "\n".join(
            f"{letra}) {q.get(f'alternativa_{letra.lower()}', '')}" for letra in "ABCDE"
        )
        enunciado = (q.get("enunciado") or "")[:1500]
        blocos.append(f"### Questao {i}\nEnunciado: {enunciado}\n{alternativas}")

    prompt = (
        "Voce classifica questoes de uma prova de Engenharia de Computacao. "
        "Para cada questao abaixo, informe o assunto principal e a dificuldade "
        "(facil, medio ou dificil, considerando um estudante de graduacao). "
        "Assuntos conhecidos (prefira um deles; crie um novo so se nenhum "
        f"servir): {', '.join(ASSUNTOS_CONHECIDOS)}. "
        f"Responda APENAS com um array JSON com {len(questoes)} objetos, na "
        "mesma ordem das questoes, no formato "
        '[{"indice": 0, "assunto": "...", "dificuldade": "facil|medio|dificil"}]'
        "\n\n" + "\n\n".join(blocos)
    )
    texto = await _chamar_gemini(prompt, json_mode=True)
    return _interpretar_classificacao(texto, len(questoes))


async def testar_conexao() -> dict:
    """Faz uma chamada minima para diagnosticar chave, modelo e limite."""
    try:
        texto = await _chamar_gemini("Responda apenas: OK", timeout=20)
    except AssistenteIAIndisponivelError as erro:
        return {"ok": False, "erro": str(erro)}
    return {"ok": True, "resposta": texto.strip()[:40]}
