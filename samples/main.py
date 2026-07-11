"""Composition root dos samples.

Executa as três features demonstrando: sucesso, erro de negócio,
curto-circuito, background e medição de tempo. O consumo dos resultados
usa ``match/case`` exaustivo com ``assert_never`` — o mypy prova que
nenhum caso de erro ficou sem tratamento.

Rode com: ``uv run task samples`` (ou ``uv run python samples/main.py``).
"""

import asyncio
import logging
from typing import assert_never

from py_return_success_or_error import ErrorGeneric, Failure, Success

from composition.container import Container
from composition.feature_registration import add_features
from features.check_connection import (
    CheckConnectionService,
    ConnectionTimeout,
    Offline,
)
from features.fibonacci import EntradaInvalida, FibonacciService
from features.sales_report import (
    BaseIndisponivel,
    SalesReportService,
    SemVendas,
)


async def demo_check_connection(service: CheckConnectionService) -> None:
    result = await service.check()
    match result:
        case Success(mensagem):
            print(f'[check_connection] {mensagem}')
        case Failure(error):
            match error:
                case Offline():
                    print(f'[check_connection] offline: {error.message}')
                case ConnectionTimeout():
                    print(f'[check_connection] timeout: {error.message}')
                case ErrorGeneric():
                    print(
                        f'[check_connection] inesperado: {error.message}'
                    )
                case _:
                    assert_never(error)
        case _:
            assert_never(result)


async def demo_fibonacci(service: FibonacciService) -> None:
    for posicao in (92, -1):
        result = await service.calcular(posicao)
        match result:
            case Success(valor):
                print(f'[fibonacci] fib({posicao}) = {valor}')
            case Failure(error):
                match error:
                    case EntradaInvalida():
                        print(
                            f'[fibonacci] entrada inválida '
                            f'({error.posicao}): {error.message}'
                        )
                    case ErrorGeneric():
                        print(f'[fibonacci] inesperado: {error.message}')
                    case _:
                        assert_never(error)
            case _:
                assert_never(result)


async def demo_sales_report(service: SalesReportService) -> None:
    for minimo in (100.0, 10_000.0):
        result = await service.gerar(minimo)
        match result:
            case Success(relatorio):
                print(
                    f'[sales_report] mínimo {minimo:.2f}: '
                    f'total={relatorio.total:.2f} '
                    f'qtd={relatorio.quantidade} '
                    f'ticket={relatorio.ticket_medio:.2f}'
                )
            case Failure(error):
                match error:
                    case SemVendas():
                        print(
                            f'[sales_report] sem vendas: {error.message}'
                        )
                    case BaseIndisponivel():
                        print(
                            f'[sales_report] base indisponível: '
                            f'{error.message}'
                        )
                    case ErrorGeneric():
                        print(
                            f'[sales_report] inesperado: {error.message}'
                        )
                    case _:
                        assert_never(error)
            case _:
                assert_never(result)


async def main() -> None:
    # exibe a medição de tempo do monitor_execution_time
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    container = add_features(Container())

    await demo_check_connection(container.resolve(CheckConnectionService))
    await demo_fibonacci(container.resolve(FibonacciService))
    await demo_sales_report(container.resolve(SalesReportService))


if __name__ == '__main__':
    asyncio.run(main())
