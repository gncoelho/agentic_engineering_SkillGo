"""Ferramentas de mercado reutilizadas pelos dois agentes."""

import httpx


def consultar_dolar() -> dict:
    """Consulta a última cotação disponível de USD para BRL.

    Use quando o usuário perguntar o valor atual do dólar americano em reais.
    Não trate o resultado como recomendação de investimento.

    Returns:
        Compra, venda, máxima, mínima, variação e horário da cotação.
    """
    try:
        resposta = httpx.get(
            "https://economia.awesomeapi.com.br/json/last/USD-BRL",
            timeout=10.0,
        )
        resposta.raise_for_status()
        cotacao = resposta.json().get("USDBRL")

        if not cotacao:
            return {
                "sucesso": False,
                "erro": "resposta_sem_cotacao",
            }

        return {
            "sucesso": True,
            "par": "USD-BRL",
            "nome": cotacao.get("name"),
            "compra": float(cotacao["bid"]),
            "venda": float(cotacao["ask"]),
            "maxima": float(cotacao["high"]),
            "minima": float(cotacao["low"]),
            "variacao_percentual": float(cotacao["pctChange"]),
            "atualizado_em": cotacao.get("create_date"),
            "fonte": "AwesomeAPI",
            "observacao": (
                "Cotação informativa; tarifas comerciais podem ser diferentes."
            ),
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as erro:
        return {
            "sucesso": False,
            "erro": "falha_api_cambio",
            "mensagem": str(erro),
        }
