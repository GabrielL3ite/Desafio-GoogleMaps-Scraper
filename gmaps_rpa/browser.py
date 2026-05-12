"""Factory de navegador Selenium usada pela automacao.

Este modulo encapsula a criacao do Chrome WebDriver com opcoes padronizadas,
timeouts e espera explicita. Com isso, o restante da aplicacao recebe uma
sessao pronta para uso sem conhecer detalhes de infraestrutura.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from gmaps_rpa import config


def create_driver() -> tuple[webdriver.Chrome, WebDriverWait]:
    """Cria e configura instancias de `WebDriver` e `WebDriverWait`.

    A funcao aplica flags de estabilidade para execucao local/headless,
    configura tempo maximo de carregamento de pagina, espera implicita global e
    retorna ambos os objetos que serao injetados no scraper.
    """
    options = webdriver.ChromeOptions()

    if config.HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=pt-BR")

    if config.CHROME_BINARY:
        options.binary_location = config.CHROME_BINARY

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(config.IMPLICIT_WAIT_SECONDS)
    wait = WebDriverWait(driver, config.ELEMENT_TIMEOUT)
    return driver, wait
