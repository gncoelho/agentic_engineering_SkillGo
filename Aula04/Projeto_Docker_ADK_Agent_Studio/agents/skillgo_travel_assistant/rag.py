"""RAG lexical local para a base privada didática da SkillGo."""

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DIRETORIO_DADOS = RAIZ_PROJETO / "data"

METADADOS_DOCUMENTOS = [
    {
        "id": "politica-viagem-001",
        "titulo": "Política de viagens da SkillGo",
        "fonte": "politica_viagens_skillgo.md",
    },
    {
        "id": "politica-cambio-001",
        "titulo": "Conversão de despesas internacionais",
        "fonte": "politica_cambio_skillgo.md",
    },
    {
        "id": "guia-clima-001",
        "titulo": "Interpretação dos dados meteorológicos",
        "fonte": "guia_clima.md",
    },
    {
        "id": "guia-fontes-001",
        "titulo": "Uso responsável de fontes",
        "fonte": "guia_fontes.md",
    },
]


def _carregar_documentos() -> list[dict]:
    """Carrega o corpus que acompanha este projeto standalone."""
    documentos = []

    for metadados in METADADOS_DOCUMENTOS:
        caminho = DIRETORIO_DADOS / metadados["fonte"]

        try:
            conteudo = caminho.read_text(encoding="utf-8").strip()
        except OSError as erro:
            raise RuntimeError(
                f"Não foi possível carregar o documento local: {caminho}"
            ) from erro

        documentos.append(
            {
                **metadados,
                "conteudo": conteudo,
            }
        )

    return documentos


DOCUMENTOS_LOCAIS = _carregar_documentos()

_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
)
_matriz_documentos = _vectorizer.fit_transform(
    [documento["conteudo"] for documento in DOCUMENTOS_LOCAIS]
)


def consultar_base_local(
    pergunta: str,
    quantidade: int = 2,
) -> dict:
    """Recupera trechos da base privada local da SkillGo.

    Use para perguntas sobre política de viagens, prestação de contas,
    interpretação de clima e regras internas de uso de fontes. Não use a
    internet para responder políticas internas.

    Args:
        pergunta: Pergunta ou tema a recuperar.
        quantidade: Número de documentos entre 1 e 3.

    Returns:
        Trechos mais próximos, fonte e score de similaridade.
    """
    pergunta = " ".join(pergunta.split())

    if not 3 <= len(pergunta) <= 300:
        return {
            "sucesso": False,
            "erro": "pergunta_invalida",
        }

    quantidade = max(1, min(int(quantidade), 3))
    vetor_pergunta = _vectorizer.transform([pergunta])
    scores = cosine_similarity(
        vetor_pergunta,
        _matriz_documentos,
    )[0]
    indices = scores.argsort()[::-1][:quantidade]
    trechos = []

    for indice in indices:
        score = float(scores[indice])
        if score < 0.05:
            continue

        documento = DOCUMENTOS_LOCAIS[int(indice)]
        trechos.append(
            {
                "id": documento["id"],
                "titulo": documento["titulo"],
                "conteudo": documento["conteudo"],
                "fonte": documento["fonte"],
                "score": round(score, 4),
            }
        )

    return {
        "sucesso": True,
        "pergunta": pergunta,
        "quantidade": len(trechos),
        "trechos": trechos,
        "metodo": "TF-IDF + similaridade de cosseno",
    }
