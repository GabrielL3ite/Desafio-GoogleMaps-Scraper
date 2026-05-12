"""Orquestrador principal da automacao.

Este modulo conecta os componentes da aplicacao: logging, criacao do browser,
execucao do scraper e exportacao de resultados. Ele representa o fluxo de alto
nivel da RPA e define os codigos de saida para sucesso e falha.
"""

from selenium.common.exceptions import WebDriverException

from gmaps_rpa import config
from gmaps_rpa.browser import create_driver
from gmaps_rpa.exporters import write_excel, write_json
from gmaps_rpa.logging_setup import setup_logging
from gmaps_rpa.scraper import GoogleMapsScraper


def run() -> int:
    """Executa o fluxo completo da automacao e retorna codigo de saida.

    Retorna:
    - `0` quando a coleta e exportacao finalizam com sucesso;
    - `1` quando ocorre erro fatal de infraestrutura ou erro inesperado.
    O bloco `finally` garante fechamento do navegador para evitar processos
    abertos apos a execucao.
    """
    logger = setup_logging(config.LOG_FILE)
    logger.info("Automacao Google Maps iniciada")

    driver = None
    try:
        driver, wait = create_driver()
        scraper = GoogleMapsScraper(driver=driver, wait=wait, logger=logger)
        records = scraper.run()

        write_json(records, config.RESULT_JSON)
        write_excel(records, config.RESULT_XLSX)

        logger.info("Total de registros: %s", len(records))
        logger.info("JSON salvo em: %s", config.RESULT_JSON)
        logger.info("XLSX salvo em: %s", config.RESULT_XLSX)
        return 0

    except WebDriverException as exc:
        logger.critical("Erro fatal de webdriver: %s", exc, exc_info=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.critical("Erro fatal inesperado: %s", exc, exc_info=True)
        return 1
    finally:
        if driver:
            driver.quit()
        logger.info("Automacao Google Maps finalizada")
