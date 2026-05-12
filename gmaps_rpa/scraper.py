"""Implementacao da coleta no Google Maps via Selenium.

Este modulo contem a classe que executa o fluxo de busca por categoria,
descoberta de links de locais, extracao dos campos de interesse e montagem dos
objetos de dominio (`PlaceRecord`).
"""

import logging
import time
from typing import List, Optional, Sequence, Tuple
from urllib.parse import quote_plus

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from gmaps_rpa import config
from gmaps_rpa.parsers import normalize_text, parse_rating_and_reviews, safe_get_first
from gmaps_rpa.types import PlaceRecord


class GoogleMapsScraper:
    """Responsavel por coletar registros de locais no Google Maps.

    A classe encapsula interacoes de browser e resiliencia contra variacoes de
    interface, centralizando tentativas de seletores e tratamento de erros de
    rede/renderizacao do Selenium.
    """

    def __init__(self, driver: WebDriver, wait: WebDriverWait, logger: logging.Logger):
        """Inicializa o scraper com dependencias injetadas.

        Parametros:
        - `driver`: sessao Selenium usada para navegar e extrair elementos;
        - `wait`: utilitario de espera explicita para sincronizar carregamento;
        - `logger`: logger compartilhado para trilha operacional e debug.
        """
        self.driver = driver
        self.wait = wait
        self.logger = logger

    def run(self) -> List[PlaceRecord]:
        """Executa o scraping completo para todas as categorias configuradas.

        Para cada categoria:
        - monta query contextualizada;
        - coleta links de locais;
        - visita cada local e extrai dados estruturados.
        Erros de um item/categoria sao registrados sem interromper toda a coleta.
        """
        collected: List[PlaceRecord] = []

        for place_type, query in config.SEARCH_QUERIES.items():
            full_query = f"{query} em {config.LOCATION_CONTEXT}" if config.LOCATION_CONTEXT else query
            self.logger.info("Buscando '%s' com query: %s", place_type, full_query)

            try:
                links = self._search_place_links(full_query)
            except (TimeoutException, WebDriverException) as exc:
                self.logger.error("Erro ao buscar links de '%s': %s", place_type, exc, exc_info=True)
                continue

            for link in links:
                try:
                    data = self._extract_place_data(link, place_type)
                    if data:
                        collected.append(data)
                except (TimeoutException, WebDriverException) as exc:
                    self.logger.warning("Ignorando local por erro de extracao: %s", exc)
                except Exception as exc:  # noqa: BLE001
                    self.logger.error("Erro inesperado ao extrair %s: %s", link, exc, exc_info=True)

        return collected

    def _search_place_links(self, query: str) -> List[str]:
        """Abre a busca no Maps e retorna links de resultados encontrados.

        Primeiro tenta acesso via URL de busca direta (`/search/?api=1`).
        Se houver timeout de renderizacao inicial, faz fallback para fluxo de
        busca pela caixa de pesquisa da home do Maps.
        """
        search_url = f"{config.GOOGLE_MAPS_URL}/search/?api=1&query={quote_plus(query)}"
        self.driver.get(search_url)

        try:
            self.wait.until(
                lambda d: d.find_elements(By.XPATH, "//div[@role='feed']")
                or d.find_elements(By.XPATH, "//a[contains(@href, '/place/')]")
            )
        except TimeoutException:
            self.driver.get(config.GOOGLE_MAPS_URL)
            search_input = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            search_input.click()
            search_input.send_keys(Keys.CONTROL, "a")
            search_input.send_keys(Keys.DELETE)
            search_input.send_keys(query)
            search_input.send_keys(Keys.ENTER)

            self.wait.until(
                lambda d: d.find_elements(By.XPATH, "//div[@role='feed']")
                or d.find_elements(By.XPATH, "//a[contains(@href, '/place/')]")
            )

        time.sleep(config.SCROLL_PAUSE_SECONDS)
        return self._collect_result_links(config.MAX_RESULTS_PER_CATEGORY)

    def _collect_result_links(self, max_results: int) -> List[str]:
        """Coleta links unicos da lista de resultados com scroll progressivo.

        O metodo limita o numero maximo de resultados e para quando:
        - atinge `max_results`;
        - nao aparecem novos links por varias rodadas seguidas.
        """
        unique_links = set()
        stagnant_rounds = 0

        for _ in range(1, 40):
            anchors = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/place/')]")
            before = len(unique_links)

            for anchor in anchors:
                href = anchor.get_attribute("href")
                if not href or "/place/" not in href:
                    continue
                unique_links.add(href.split("?")[0])

            if len(unique_links) >= max_results:
                break

            if len(unique_links) == before:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0

            if stagnant_rounds >= config.MAX_SCROLL_ROUNDS_WITHOUT_NEW_RESULTS:
                break

            self._scroll_results_panel()
            time.sleep(config.SCROLL_PAUSE_SECONDS)

        return list(unique_links)[:max_results]

    def _scroll_results_panel(self) -> None:
        """Realiza scroll no painel de resultados ou na janela principal.

        Em layouts com feed lateral, rola o container especifico.
        Como fallback, rola a janela para tentar forcar carregamento de itens.
        """
        panels = self.driver.find_elements(By.XPATH, "//div[@role='feed']")
        if panels:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", panels[0])
            return
        self.driver.execute_script("window.scrollBy(0, 1000);")

    def _extract_place_data(self, place_url: str, place_type: str) -> Optional[PlaceRecord]:
        """Extrai dados de um local e retorna `PlaceRecord` quando valido.

        O metodo tenta multiplos seletores para nome, nota e avaliacoes, pois a
        UI do Google Maps muda com frequencia. Se nome nao for encontrado,
        considera o registro invalido e retorna `None`.
        """
        self.driver.get(place_url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        name = self._first_text(
            [
                (By.CSS_SELECTOR, "h1.DUwDvf"),
                (By.CSS_SELECTOR, "h1.fontHeadlineLarge"),
                (By.TAG_NAME, "h1"),
            ]
        )

        rating_text = self._first_text(
            [
                (By.CSS_SELECTOR, "span.MW4etd"),
                (By.XPATH, "//div[contains(@class,'F7nice')]//span[contains(@aria-hidden,'true')]"),
            ]
        )

        reviews_text = self._first_text(
            [
                (By.CSS_SELECTOR, "button[jsaction*='pane.rating.moreReviews']"),
                (By.CSS_SELECTOR, "span.UY7F9"),
                (By.XPATH, "//button[contains(@jsaction,'pane.rating.moreReviews')]"),
                (By.XPATH, "//button[contains(@aria-label,'avaliac')]"),
                (By.XPATH, "//button[contains(@aria-label,'review')]"),
            ]
        )

        address = self._extract_address()
        if not name:
            return None

        rating, reviews = parse_rating_and_reviews(rating_text, reviews_text)
        return PlaceRecord(
            nome=name,
            tipo=place_type,
            nota=rating,
            quantidade_avaliacoes=reviews,
            endereco=address,
        )

    def _extract_address(self) -> str:
        """Extrai e normaliza endereco textual a partir de diferentes seletores."""
        address = self._first_text(
            [
                (By.CSS_SELECTOR, "button[data-item-id='address'] div.fontBodyMedium"),
                (By.CSS_SELECTOR, "button[data-item-id='address']"),
                (By.XPATH, "//button[contains(@aria-label,'Endere')]"),
                (By.XPATH, "//button[contains(@aria-label,'Address')]"),
            ]
        )

        for prefix in ("Endereco:", "Endereco :", "Endereço:", "Address:"):
            if address.lower().startswith(prefix.lower()):
                return normalize_text(address[len(prefix) :])
        return address

    def _first_text(self, selectors: Sequence[Tuple[By, str]]) -> str:
        """Retorna o primeiro texto util a partir de uma lista de seletores.

        Para cada seletor, tenta tanto `element.text` quanto `aria-label`, pois
        alguns campos do Maps aparecem em uma ou outra forma.
        """
        for by, selector in selectors:
            elements = self.driver.find_elements(by, selector)
            values = []
            for element in elements:
                values.append(element.text)
                values.append(element.get_attribute("aria-label"))
            chosen = safe_get_first(values)
            if chosen:
                return chosen
        return ""
