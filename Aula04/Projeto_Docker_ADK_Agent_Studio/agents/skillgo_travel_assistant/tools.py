"""Ferramentas externas do SkillGo Travel Assistant."""

from ddgs import DDGS
import httpx

from shared.market_tools import consultar_dolar


def buscar_na_internet(
    consulta: str,
    max_resultados: int = 3,
) -> dict:
    """Pesquisa informações atuais na internet.

    Use quando a pergunta depender de notícias, eventos recentes, páginas
    públicas ou informações que podem ter mudado depois do treinamento do
    modelo. Não use para políticas internas da SkillGo.

    Args:
        consulta: Termos objetivos da pesquisa.
        max_resultados: Quantidade entre 1 e 5.

    Returns:
        Resultados com título, resumo e URL, ou erro estruturado.
    """
    consulta = " ".join(consulta.split())

    if not 3 <= len(consulta) <= 200:
        return {
            "sucesso": False,
            "erro": "consulta_invalida",
            "mensagem": "A consulta deve ter entre 3 e 200 caracteres.",
        }

    max_resultados = max(1, min(int(max_resultados), 5))

    try:
        itens = list(
            DDGS().text(
                consulta,
                max_results=max_resultados,
            )
        )
        resultados = [
            {
                "titulo": item.get("title"),
                "resumo": item.get("body"),
                "url": item.get("href"),
            }
            for item in itens
        ]
        return {
            "sucesso": True,
            "consulta": consulta,
            "quantidade": len(resultados),
            "resultados": resultados,
            "fonte": "DDGS",
        }
    except Exception as erro:
        return {
            "sucesso": False,
            "erro": "falha_busca",
            "mensagem": str(erro),
        }


def _descrever_codigo_wmo(codigo: int) -> str:
    if codigo == 0:
        return "céu limpo"
    if codigo in {1, 2, 3}:
        return "parcialmente nublado ou nublado"
    if codigo in {45, 48}:
        return "neblina"
    if codigo in {51, 53, 55, 56, 57}:
        return "garoa"
    if codigo in {61, 63, 65, 66, 67}:
        return "chuva"
    if codigo in {71, 73, 75, 77}:
        return "neve"
    if codigo in {80, 81, 82}:
        return "pancadas de chuva"
    if codigo in {85, 86}:
        return "pancadas de neve"
    if codigo in {95, 96, 99}:
        return "trovoada"
    return "condição não classificada"


def consultar_clima(cidade: str) -> dict:
    """Consulta as condições meteorológicas atuais de uma cidade.

    Use quando o usuário perguntar temperatura, sensação térmica, chuva,
    umidade ou vento em uma localidade.

    Args:
        cidade: Cidade e, quando necessário, estado ou país.

    Returns:
        Local encontrado, dados atuais, unidades e fontes.
    """
    cidade = " ".join(cidade.split())

    if not 2 <= len(cidade) <= 100:
        return {
            "sucesso": False,
            "erro": "cidade_invalida",
        }

    try:
        geocoding = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": cidade,
                "count": 1,
                "language": "pt",
                "format": "json",
            },
            timeout=10.0,
        )
        geocoding.raise_for_status()
        locais = geocoding.json().get("results") or []

        if not locais:
            return {
                "sucesso": False,
                "erro": "cidade_nao_encontrada",
                "cidade_consultada": cidade,
            }

        local = locais[0]
        meteo = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": local["latitude"],
                "longitude": local["longitude"],
                "current": (
                    "temperature_2m,apparent_temperature,"
                    "relative_humidity_2m,precipitation,"
                    "weather_code,wind_speed_10m"
                ),
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=10.0,
        )
        meteo.raise_for_status()
        dados = meteo.json()
        atual = dados.get("current") or {}
        unidades = dados.get("current_units") or {}
        codigo = int(atual.get("weather_code", -1))

        return {
            "sucesso": True,
            "local": {
                "cidade": local.get("name"),
                "estado": local.get("admin1"),
                "pais": local.get("country"),
                "latitude": local.get("latitude"),
                "longitude": local.get("longitude"),
                "timezone": dados.get("timezone"),
            },
            "observado_em": atual.get("time"),
            "condicao": _descrever_codigo_wmo(codigo),
            "temperatura": {
                "valor": atual.get("temperature_2m"),
                "unidade": unidades.get("temperature_2m"),
            },
            "sensacao_termica": {
                "valor": atual.get("apparent_temperature"),
                "unidade": unidades.get("apparent_temperature"),
            },
            "umidade_relativa": {
                "valor": atual.get("relative_humidity_2m"),
                "unidade": unidades.get("relative_humidity_2m"),
            },
            "precipitacao": {
                "valor": atual.get("precipitation"),
                "unidade": unidades.get("precipitation"),
            },
            "vento": {
                "valor": atual.get("wind_speed_10m"),
                "unidade": unidades.get("wind_speed_10m"),
            },
            "fonte": "Open-Meteo",
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as erro:
        return {
            "sucesso": False,
            "erro": "falha_api_clima",
            "mensagem": str(erro),
        }


__all__ = [
    "buscar_na_internet",
    "consultar_clima",
    "consultar_dolar",
]
