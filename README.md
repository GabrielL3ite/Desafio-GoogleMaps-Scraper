# Desafio Google Maps (RPA com Selenium)

Este projeto automatiza buscas no Google Maps por categorias definidas em configuracao, coleta dados dos locais encontrados e gera saidas em `JSON` e `XLSX`.

Hoje o fluxo faz:
- abertura do Google Maps;
- busca por categorias (ex.: academia, restaurante, sorveteria, hotel);
- extracao de `nome`, `tipo`, `nota`, `quantidade_avaliacoes` e `endereco`;
- exportacao dos resultados para arquivos.

## Requisitos

- Python `3.9+`
- Google Chrome instalado
- Conexao com internet

## Dependencias Python

Dependencias declaradas em [requirements.txt](<c:\Users\elain\OneDrive\Documentos\Desafio GoogleMaps\requirements.txt>):

- `selenium>=4.20.0`
- `openpyxl>=3.1.2`

## Instalacao

No diretorio raiz do projeto:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Execucao

Com o ambiente virtual ativo:

```bash
python main.py
```

Arquivos gerados na raiz do projeto:
- `automation.log`
- `resultados.json`
- `resultados.xlsx`

## O que alterar em outro computador

As configuracoes ficam em [config.py](<c:\Users\elain\OneDrive\Documentos\Desafio GoogleMaps\gmaps_rpa\config.py>).

Campos mais importantes para ajustar:

- `LOCATION_CONTEXT`: cidade/regiao da busca (ex.: `"Sao Paulo, SP"`).
- `SEARCH_QUERIES`: categorias e termos pesquisados.
- `MAX_RESULTS_PER_CATEGORY`: quantidade maxima de locais por categoria.
- `HEADLESS`: `True` para rodar sem abrir janela do navegador, `False` para visualizar.
- `CHROME_BINARY`: caminho do executavel do Chrome se o Selenium nao localizar automaticamente.
  - Exemplo Windows: `r"C:\Program Files\Google\Chrome\Application\chrome.exe"`
- Timeouts:
  - `PAGE_LOAD_TIMEOUT`
  - `ELEMENT_TIMEOUT`
  - `IMPLICIT_WAIT_SECONDS`
  - `SCROLL_PAUSE_SECONDS`

Observacao sobre caminhos locais:
- `LOG_FILE`, `RESULT_JSON` e `RESULT_XLSX` usam `BASE_DIR` automaticamente, entao nao precisam ser alterados na maioria dos casos.

## Sugestao de estrutura de pastas

```text
Desafio GoogleMaps/
|-- main.py
|-- requirements.txt
|-- README.md
|-- automation.log
|-- resultados.json
|-- resultados.xlsx
`-- gmaps_rpa/
    |-- __init__.py
    |-- app.py
    |-- browser.py
    |-- config.py
    |-- exporters.py
    |-- logging_setup.py
    |-- parsers.py
    |-- scraper.py
    `-- types.py
```

## Fluxo rapido para novos testes

1. Ajuste `LOCATION_CONTEXT` e `SEARCH_QUERIES`.
2. Execute `python main.py`.
3. Valide os arquivos `resultados.json` e `resultados.xlsx`.
4. Consulte `automation.log` se houver erro de coleta.
