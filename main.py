"""Entry point do projeto.

Este modulo inicia a aplicacao de automacao de Google Maps de forma controlada.
Ele importa a funcao `run` do modulo de orquestracao e converte seu retorno em
codigo de saida de processo, permitindo integracao simples com terminal e CI.
"""

from gmaps_rpa.app import run


if __name__ == "__main__":
    raise SystemExit(run())
