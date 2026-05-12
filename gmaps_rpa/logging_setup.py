"""Configuracao de logging da aplicacao.

Este modulo padroniza formato e destinos de log para toda a automacao,
gravando detalhes em arquivo e mensagens operacionais no console.
"""

import logging
from pathlib import Path


def setup_logging(log_path: Path) -> logging.Logger:
    """Cria e retorna logger nomeado `gmaps_rpa` com handlers idempotentes.

    A configuracao inclui:
    - arquivo em nivel `DEBUG` para diagnostico completo;
    - console em nivel `INFO` para acompanhamento de execucao.
    Quando handlers ja existem, a funcao devolve o logger atual para evitar
    duplicacao de logs em chamadas repetidas.
    """
    logger = logging.getLogger("gmaps_rpa")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
