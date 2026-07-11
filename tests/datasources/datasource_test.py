"""Testes da porta de dados."""

from dataclasses import dataclass

import pytest

from py_return_success_or_error.datasources.datasource import DataSource
from py_return_success_or_error.parameters.parameters import Parameters


@dataclass(frozen=True)
class ConsultaParameters(Parameters):
    chave: str


class ConsultaDataSource(DataSource[str, ConsultaParameters]):
    """Datasource fake: devolve o dado bruto ou lança a exceção técnica."""

    def __init__(self, *, falha: Exception | None = None) -> None:
        self._falha = falha

    async def __call__(self, parameters: ConsultaParameters) -> str:
        if self._falha is not None:
            raise self._falha
        return f'dado[{parameters.chave}]'


async def test_sucesso_devolve_dado_bruto() -> None:
    datasource = ConsultaDataSource()
    assert await datasource(ConsultaParameters(chave='k1')) == 'dado[k1]'


async def test_falha_lanca_excecao_tecnica() -> None:
    datasource = ConsultaDataSource(falha=TimeoutError('rede fora'))
    with pytest.raises(TimeoutError):
        await datasource(ConsultaParameters(chave='k1'))
