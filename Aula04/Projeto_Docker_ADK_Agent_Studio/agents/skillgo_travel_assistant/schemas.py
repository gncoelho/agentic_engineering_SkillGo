"""Contratos Pydantic da fronteira de entrada."""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


class EntradaAgente(BaseModel):
    """Entrada aceita pelo agente antes da chamada ao modelo."""

    model_config = ConfigDict(str_strip_whitespace=True)

    usuario_id: str = Field(
        min_length=3,
        max_length=40,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    pergunta: str = Field(
        min_length=5,
        max_length=500,
    )

    @field_validator("pergunta")
    @classmethod
    def normalizar_pergunta(cls, valor: str) -> str:
        if "\x00" in valor:
            raise ValueError("A pergunta contém caractere nulo.")
        return " ".join(valor.split())
