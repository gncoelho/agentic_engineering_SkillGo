"""Servidor A2A do especialista remoto em câmbio."""

import os

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from shared.market_tools import consultar_dolar


MODEL_NAME = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
A2A_PUBLIC_URL = os.getenv(
    "A2A_PUBLIC_URL",
    "http://127.0.0.1:8001",
)

root_agent = Agent(
    name="especialista_cambio",
    model=MODEL_NAME,
    description=(
        "Especialista remoto em cotação USD-BRL e interpretação de câmbio."
    ),
    instruction="""
Você é um especialista em câmbio USD-BRL.

REGRAS
1. Para qualquer pergunta sobre cotação atual, use consultar_dolar.
2. Informe compra, venda, fonte e horário quando disponíveis.
3. Explique que a cotação é informativa e não inclui tarifas comerciais.
4. Não forneça recomendação de investimento.
5. Se a ferramenta falhar, declare a indisponibilidade.
6. Responda em português do Brasil.
""",
    tools=[consultar_dolar],
)

agent_card = AgentCard(
    name="especialista_cambio",
    description=(
        "Especialista remoto em cotação USD-BRL e interpretação de câmbio."
    ),
    supported_interfaces=[
        AgentInterface(
            url=A2A_PUBLIC_URL,
            protocol_binding="JSONRPC",
            protocol_version="1.0",
        )
    ],
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
    ),
    skills=[
        AgentSkill(
            id="consultar_cambio_usd_brl",
            name="Consultar câmbio USD-BRL",
            description=(
                "Consulta a cotação atual do dólar comercial em reais e "
                "explica os valores retornados."
            ),
            tags=["cambio", "usd", "brl"],
            examples=["Qual é a cotação atual do dólar?"],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
)

a2a_app = to_a2a(
    root_agent,
    port=8001,
    agent_card=agent_card,
)
