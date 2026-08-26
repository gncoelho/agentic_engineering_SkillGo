"""Agente selecionável no Studio para demonstrar a delegação A2A."""

import os

from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


MODEL_NAME = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
AGENT_CARD_URL = os.getenv(
    "A2A_EXCHANGE_CARD_URL",
    "http://127.0.0.1:8001/.well-known/agent-card.json",
)

especialista_remoto = RemoteA2aAgent(
    name="especialista_cambio_remoto",
    description=(
        "Agente remoto que consulta e explica a cotação atual USD-BRL."
    ),
    agent_card=AGENT_CARD_URL,
    timeout=30.0,
)

root_agent = Agent(
    name="coordenador_a2a",
    model=MODEL_NAME,
    description=(
        "Coordena perguntas de câmbio e delega a um especialista via A2A."
    ),
    instruction="""
Você é um coordenador de agentes.

Quando a pergunta envolver dólar, USD-BRL ou câmbio:
1. delegue ao especialista_cambio_remoto;
2. preserve fonte, valores e horário da resposta remota;
3. informe que a análise veio do especialista;
4. se o especialista estiver indisponível, declare a falha;
5. nunca invente uma cotação.

Para perguntas fora de câmbio, explique que este coordenador demonstra
somente o fluxo A2A de câmbio.

Responda em português do Brasil.
""",
    sub_agents=[especialista_remoto],
)
