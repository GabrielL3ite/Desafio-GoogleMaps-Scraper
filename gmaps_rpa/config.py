"""Configuracoes centrais da automacao.

Este modulo define constantes de ambiente, parametros de busca, limites de
coleta, timeouts de Selenium e caminhos de saida. A ideia e concentrar valores
ajustaveis em um unico lugar para facilitar manutencao e testes.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_MAPS_URL = "https://www.google.com/maps"
SEARCH_QUERIES = {
    "academia": "academias",
    "restaurante": "restaurantes",
    "sorveteria": "sorveterias",
    "hotel": "hotéis",
}

LOCATION_CONTEXT = "Uberlandia, MG"
MAX_RESULTS_PER_CATEGORY = 5

PAGE_LOAD_TIMEOUT = 30
ELEMENT_TIMEOUT = 20
IMPLICIT_WAIT_SECONDS = 2
SCROLL_PAUSE_SECONDS = 1.5
MAX_SCROLL_ROUNDS_WITHOUT_NEW_RESULTS = 4

HEADLESS = True
CHROME_BINARY = None

LOG_FILE = BASE_DIR / "automation.log"
RESULT_JSON = BASE_DIR / "resultados.json"
RESULT_XLSX = BASE_DIR / "resultados.xlsx"
