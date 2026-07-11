"""Testes da camada anticorrupção."""

import asyncio
from dataclasses import dataclass

import pytest

from py_return_success_or_error.datasources.datasource import DataSource
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.repositories.repository_base import (
    RepositoryBase,
)
from tests.helpers.assertions import assert_failure, assert_success
from tests.helpers.test_errors import NotFoundError, TestError, UnexpectedError


@dataclass(frozen=True)
class ConsultaParameters(Parameters):
    chave: str


class ConsultaDataSource(DataSource[str, ConsultaParameters]):
    def __init__(self, *, falha: BaseException | None = None) -> None:
        self._falha = falha
        self.parametros_recebidos: ConsultaParameters | None = None

    async def __call__(self, parameters: ConsultaParameters) -> str:
        self.parametros_recebidos = parameters
        if self._falha is not None:
            raise self._falha
        return f'dado[{parameters.chave}]'


class ConsultaRepository(
    RepositoryBase[str, ConsultaParameters, TestError]
):
    def __init__(self, datasource: ConsultaDataSource) -> None:
        super().__init__(datasource)
        self.map_error_chamado = False

    def map_error(
        self, exception: Exception, parameters: ConsultaParameters
    ) -> TestError:
        self.map_error_chamado = True
        match exception:
            case KeyError():
                return NotFoundError(
                    message=f'chave {parameters.chave} não encontrada'
                )
            case _:
                return UnexpectedError(message=str(exception))


async def test_sucesso_embrulha_em_success() -> None:
    repository = ConsultaRepository(ConsultaDataSource())
    result = await repository(ConsultaParameters(chave='k1'))
    assert assert_success(result) == 'dado[k1]'


async def test_excecao_traduzida_pelo_map_error() -> None:
    repository = ConsultaRepository(
        ConsultaDataSource(falha=KeyError('k1'))
    )
    result = await repository(ConsultaParameters(chave='k1'))
    assert assert_failure(result) == NotFoundError(
        message='chave k1 não encontrada'
    )


async def test_braco_default_do_map_error() -> None:
    repository = ConsultaRepository(
        ConsultaDataSource(falha=OSError('disco cheio'))
    )
    result = await repository(ConsultaParameters(chave='k1'))
    assert assert_failure(result) == UnexpectedError(message='disco cheio')


async def test_cancelamento_propaga_sem_passar_pelo_map_error() -> None:
    repository = ConsultaRepository(
        ConsultaDataSource(falha=asyncio.CancelledError())
    )
    with pytest.raises(asyncio.CancelledError):
        await repository(ConsultaParameters(chave='k1'))
    assert repository.map_error_chamado is False


async def test_parametros_chegam_ao_datasource() -> None:
    datasource = ConsultaDataSource()
    repository = ConsultaRepository(datasource)
    params = ConsultaParameters(chave='k9')
    await repository(params)
    assert datasource.parametros_recebidos is params
