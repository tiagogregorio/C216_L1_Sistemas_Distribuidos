"""Tratamento de erros inesperados (500) que preserva os headers de CORS.

Sem isso, um erro 500 chega ao navegador SEM Access-Control-Allow-Origin (o
ServerErrorMiddleware do Starlette fica por fora do CORSMiddleware) e o
frontend so ve "NetworkError"/"Failed to fetch", escondendo a causa real.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.erros")


def registrar_tratamento_de_erros(app: FastAPI, origens_permitidas: list[str]) -> None:
    @app.exception_handler(Exception)
    async def erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro inesperado em %s %s", request.method, request.url.path)

        cabecalhos = {}
        origem = request.headers.get("origin")
        if origem and (origem in origens_permitidas or "*" in origens_permitidas):
            cabecalhos = {
                "Access-Control-Allow-Origin": origem,
                "Access-Control-Allow-Credentials": "true",
                "Vary": "Origin",
            }

        resumo = (str(exc).splitlines() or [""])[0][:200]
        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    f"Erro interno do servidor ({type(exc).__name__}): {resumo} "
                    "— veja: docker compose logs backend"
                )
            },
            headers=cabecalhos,
        )
