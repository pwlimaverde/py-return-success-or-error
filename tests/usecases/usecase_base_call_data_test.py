"""Testes do caso de uso com dados."""

import asyncio
from dataclasses import dataclass
from datetime import timedelta

import pytest

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
)
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.repositories.repository import Repository
from py_return_success_or_error.usecases.usecase_base_call_data import (
    UsecaseBaseCallData,
)
from tests.helpers.assertions import assert_failure, assert_success
from tests.helpers.test_errors import (
    NotFoundError,
    TestError,
    UnexpectedError,
    ValidationError,
)


@dataclass(frozen=True)
class RelatorioParameters(Parameters):
    minimo: int


class VendasRepositoryFake(
    Repository[list[int], RelatorioParameters, TestError]
):
    """Repositório fake: devolve o resultado programado."""

    def __init__(
        self,
        resultado: ReturnSuccessOrError[list[int], TestError],
        *,
        cancelar: bool = False,
    ) -> None:
        self._resultado = resultado
        self._cancelar = cancelar

    async def __call__(
        self, parameters: RelatorioParameters
    ) -> ReturnSuccessOrError[list[int], TestError]:
        if self._cancelar:
            raise asyncio.CancelledError()
        return self._resultado


class SomaVendasUsecase(
    UsecaseBaseCallData[int, list[int], RelatorioParameters, TestError]
):
    """Soma as vendas acima do mínimo; lista vazia é erro de negócio."""

    def __init__(
        self,
        repository: Repository[list[int], RelatorioParameters, TestError],
        *,
        run_in_background: bool = False,
        monitor_execution_time: bool = False,
        excecao: BaseException | None = None,
    ) -> None:
        super().__init__(
            repository,
            run_in_background=run_in_background,
            monitor_execution_time=monitor_execution_time,
        )
        self._excecao = excecao
        self.process_chamado = False
        self.tempo_medido: timedelta | None = None

    def process(
        self, data: list[int], parameters: RelatorioParameters
    ) -> ReturnSuccessOrError[int, TestError]:
        self.process_chamado = True
        if self._excecao is not None:
            raise self._excecao
        if not data:
            return self.fail(
                ValidationError(message='sem vendas', field='data')
            )
        return self.ok(
            sum(venda for venda in data if venda >= parameters.minimo)
        )

    def on_unexpected(self, exception: Exception) -> TestError:
        return UnexpectedError(message=str(exception))

    def on_execution_time_measured(self, elapsed: timedelta) -> None:
        self.tempo_medido = elapsed


async def test_sucesso_processa_o_dado_do_fetch() -> None:
    usecase = SomaVendasUsecase(VendasRepositoryFake(Success([5, 10, 3])))
    result = await usecase(RelatorioParameters(minimo=5))
    assert assert_success(result) == 15


async def test_fetch_falho_curto_circuita_sem_chamar_o_process() -> None:
    erro = NotFoundError(message='sem base')
    usecase = SomaVendasUsecase(VendasRepositoryFake(Failure(erro)))
    result = await usecase(RelatorioParameters(minimo=0))
    assert assert_failure(result) == erro
    assert usecase.process_chamado is False


async def test_caso_concreto_do_erro_do_fetch_e_preservado() -> None:
    erro = NotFoundError(message='sem base')
    usecase = SomaVendasUsecase(VendasRepositoryFake(Failure(erro)))
    result = await usecase(RelatorioParameters(minimo=0))
    assert isinstance(assert_failure(result), NotFoundError)


async def test_erro_de_negocio_do_process() -> None:
    usecase = SomaVendasUsecase(VendasRepositoryFake(Success([])))
    result = await usecase(RelatorioParameters(minimo=0))
    assert assert_failure(result) == ValidationError(
        message='sem vendas', field='data'
    )


@pytest.mark.parametrize('background', [False, True])
async def test_excecao_inesperada_vira_on_unexpected(
    background: bool,
) -> None:
    usecase = SomaVendasUsecase(
        VendasRepositoryFake(Success([1])),
        run_in_background=background,
        excecao=RuntimeError('bug'),
    )
    result = await usecase(RelatorioParameters(minimo=0))
    assert assert_failure(result) == UnexpectedError(message='bug')


async def test_paridade_direto_background() -> None:
    params = RelatorioParameters(minimo=2)
    direto = await SomaVendasUsecase(
        VendasRepositoryFake(Success([1, 2, 3]))
    )(params)
    background = await SomaVendasUsecase(
        VendasRepositoryFake(Success([1, 2, 3])), run_in_background=True
    )(params)
    assert direto == background


async def test_monitor_chama_o_hook_e_preserva_o_resultado() -> None:
    usecase = SomaVendasUsecase(
        VendasRepositoryFake(Success([4])), monitor_execution_time=True
    )
    result = await usecase(RelatorioParameters(minimo=0))
    assert assert_success(result) == 4
    assert usecase.tempo_medido is not None


async def test_cancelamento_no_fetch_propaga() -> None:
    usecase = SomaVendasUsecase(
        VendasRepositoryFake(Success([1]), cancelar=True)
    )
    with pytest.raises(asyncio.CancelledError):
        await usecase(RelatorioParameters(minimo=0))
    assert usecase.process_chamado is False


async def test_cancelamento_pendente_impede_o_fetch_e_o_process() -> None:
    usecase = SomaVendasUsecase(VendasRepositoryFake(Success([1])))
    task = asyncio.create_task(usecase(RelatorioParameters(minimo=0)))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert usecase.process_chamado is False
