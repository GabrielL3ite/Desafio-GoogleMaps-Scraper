"""Utilitarios de parsing e normalizacao de texto numerico.

Este modulo concentra regras para limpar strings vindas da UI do Google Maps e
converter valores de nota/avaliacoes em tipos numericos confiaveis.
"""

import re
from typing import Iterable, Optional, Tuple


def normalize_text(value: Optional[str]) -> str:
    """Normaliza texto removendo espacos redundantes e valores vazios."""
    if not value:
        return ""
    return " ".join(value.split())


def safe_get_first(values: Iterable[Optional[str]]) -> str:
    """Retorna o primeiro valor textual util apos normalizacao.

    E usado quando o scraper tenta multiplos seletores e precisa do primeiro
    texto valido, ignorando `None`, strings vazias e espacos.
    """
    for value in values:
        normalized = normalize_text(value)
        if normalized:
            return normalized
    return ""


def parse_number(value: str) -> Optional[float]:
    """Converte string numerica em `float`, tolerando formatos locais.

    A funcao aceita separadores `,` e `.` em diferentes padroes e remove
    caracteres nao numericos comuns em labels de interface.
    """
    if not value:
        return None

    cleaned = re.sub(r"[^0-9,.-]", "", value).strip()
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        if cleaned.count(",") == 1:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_reviews_count(value: str) -> Optional[int]:
    """Extrai quantidade de avaliacoes a partir de textos heterogeneos.

    A extracao tenta, nesta ordem:
    - numero entre parenteses;
    - numero antes de palavras como `avaliac` ou `review`;
    - maior candidato numerico encontrado no texto.
    """
    if not value:
        return None

    text = normalize_text(value)
    if not text:
        return None

    in_parenthesis = re.search(r"\(([0-9][0-9\.,\s]*)\)", text)
    if in_parenthesis:
        parsed = _parse_integer_token(in_parenthesis.group(1))
        if parsed is not None:
            return parsed

    by_label = re.search(r"([0-9][0-9\.,\s]*)\s*(?:avaliac|review)", text.lower())
    if by_label:
        parsed = _parse_integer_token(by_label.group(1))
        if parsed is not None:
            return parsed

    candidates = re.findall(r"[0-9][0-9\.,\s]*", text)
    parsed_values = [v for v in (_parse_integer_token(token) for token in candidates) if v is not None]
    if parsed_values:
        return max(parsed_values)

    return None


def _parse_integer_token(token: str) -> Optional[int]:
    """Converte token textual em inteiro, removendo separadores e ruido."""
    cleaned = re.sub(r"[^0-9]", "", token)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def parse_rating_and_reviews(rating_text: str, reviews_text: str) -> Tuple[Optional[float], Optional[int]]:
    """Converte textos de nota e avaliacoes para tipos numericos do dominio."""
    rating = parse_number(rating_text)
    reviews = parse_reviews_count(reviews_text)
    return rating, reviews
