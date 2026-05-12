"""Camada de exportacao dos resultados coletados.

Este modulo transforma uma sequencia de registros em artefatos de saida nos
formatos JSON e XLSX. Assim, o scraper permanece focado em coleta, enquanto a
serializacao e apresentacao tabular ficam centralizadas aqui.
"""

import json
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from gmaps_rpa.types import PlaceRecord


def write_json(data: Iterable[PlaceRecord], output_path: Path) -> None:
    """Persiste os registros em arquivo JSON UTF-8 formatado.

    Cada `PlaceRecord` e convertido para dicionario por `to_dict`, permitindo
    serializacao limpa e legivel para consumo humano ou integracoes.
    """
    with output_path.open("w", encoding="utf-8") as file:
        json.dump([row.to_dict() for row in data], file, ensure_ascii=False, indent=2)


def write_excel(data: Iterable[PlaceRecord], output_path: Path) -> None:
    """Gera planilha XLSX com cabecalho, dados e ajuste basico de largura.

    A funcao cria a aba `Resultados`, escreve colunas padrao do dominio,
    aplica estilo simples no cabecalho e ajusta largura para melhorar leitura.
    """
    rows = list(data)

    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"

    headers = ["nome", "tipo", "nota", "quantidade_avaliacoes", "endereco"]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        ws.append([row.nome, row.tipo, row.nota, row.quantidade_avaliacoes, row.endereco])

    for column in ws.columns:
        max_len = 0
        column_letter = column[0].column_letter
        for cell in column:
            value = str(cell.value) if cell.value is not None else ""
            if len(value) > max_len:
                max_len = len(value)
        ws.column_dimensions[column_letter].width = min(max_len + 4, 80)

    wb.save(output_path)
