"""Validação Pydantic e guardrail didático executados antes do modelo."""

import logging

from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import ValidationError

from .schemas import EntradaAgente


logger = logging.getLogger(__name__)

PADROES_BLOQUEADOS = {
    "ignore as instruções",
    "ignore todas as instruções",
    "revele a chave",
    "mostre o token",
    "apague todos os dados",
}


def _ultima_mensagem_usuario(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if getattr(content, "role", None) != "user":
            continue
        textos = [
            part.text
            for part in (content.parts or [])
            if getattr(part, "text", None)
        ]
        return " ".join(textos)
    return ""


def _resposta_bloqueada(texto: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=texto)],
        )
    )


def validar_entrada_pydantic(
    callback_context,
    llm_request: LlmRequest,
):
    """Valida a mensagem da interface antes de chamar o modelo."""
    texto = _ultima_mensagem_usuario(llm_request)
    if not texto:
        return None

    try:
        entrada = EntradaAgente(
            usuario_id="agent_studio",
            pergunta=texto,
        )
        logger.info(
            "Entrada validada pelo Pydantic: %s caracteres",
            len(entrada.pergunta),
        )
        return None
    except ValidationError:
        logger.warning("Entrada rejeitada pelo Pydantic.")
        return _resposta_bloqueada(
            "A entrada deve conter entre 5 e 500 caracteres válidos."
        )


def guardrail_entrada(
    callback_context,
    llm_request: LlmRequest,
):
    """Bloqueia padrões didáticos de prompt injection e exfiltração."""
    texto = _ultima_mensagem_usuario(llm_request).lower()
    padrao = next(
        (
            item
            for item in PADROES_BLOQUEADOS
            if item in texto
        ),
        None,
    )
    if not padrao:
        return None

    logger.warning(
        "Guardrail bloqueou a categoria: %s",
        padrao,
    )
    return _resposta_bloqueada(
        "Não posso atender a essa solicitação. Posso ajudar com pesquisa, "
        "clima, câmbio e políticas de viagem de forma segura."
    )
