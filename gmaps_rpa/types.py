"""Modelos de dados do dominio de scraping.

Este modulo define estruturas tipadas para representar cada local coletado,
facilitando validacao, serializacao e manutencao do contrato de dados.
"""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class PlaceRecord:
    """Representa um local extraido do Google Maps em formato estruturado."""

    nome: str
    tipo: str
    nota: Optional[float]
    quantidade_avaliacoes: Optional[int]
    endereco: str

    def to_dict(self) -> dict:
        """Converte o registro para dicionario simples serializavel."""
        return asdict(self)
