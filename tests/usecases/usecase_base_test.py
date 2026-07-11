"""Testes do caso de uso puro."""

import asyncio
from dataclasses import dataclass
from datetime import timedelta

import pytest

from py_return_success_or_error.core.nil import NIL, Nil
from py_return_success_or_error.core.return_success_or_error import (
    ReturnSuccessOrError,
)
from py_return_success_or_error.core.unit import UNIT, Unit
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.usecases.usecase_base import UsecaseBase
from tests.helpers.assertions import assert_failure, assert_success
from tests.helpers.test_errors import (
    TestError,
    UnexpectedError,
    ValidationError,
)


@dataclass(frozen=True)
class NumeroParameters(Parameters):
    numero: int


class DobroUsecase(UsecaseBase[int, NumeroParameters, TestError]):
    """Dobra o número; negativo é erro de negócio; None simulado é bug."""

    def __init__(
        self,
        *,
        run_in_background: bool = False,
        monitor_execution_time: bool = False,
        excecao: BaseException | None = None,
    ) -> None:
        super().__init__(
            run_in_background=run_in_background,
            monitor_execution_time=monitor_execution_time,
        )
        self._excecao = excecao
        self.process_chamado = False
        self.tempo_medido: timedelta | None = None

    def process(
        self, parameters: NumeroParameters
    ) -> ReturnSuccessOrError[int, TestError]:
        self.process_chamado = True
        if self._excecao is not None:
            raise self._excecao
        if parameters.numero < 0:
            return self.fail(
                ValidationError(message='negativo', field='numero')
            )
        return self.ok(parameters.numero * 2)

    def on_unexpected(self, exception: Exception) -> TestError:
        return UnexpectedError(message=str(exception))

    def on_execution_time_measured(self, elapsed: timedelta) -> None:
        self.tempo_medido = elapsed


class VoidUsecase(UsecaseBase[Unit, NumeroParameters, TestError]):
    def process(
        self, parameters: NumeroParameters
    ) -> ReturnSuccessOrError[Unit, TestError]:
        return self.ok(UNIT)

    def on_unexpected(self, exception: Exception) -> TestError:
        return UnexpectedError(message=str(exception))


class BuscaOpcionalUsecase(
    UsecaseBase[int | Nil, NumeroParameters, TestError]
):
    """Nil como resultado válido: "não encontrado" não é falha."""

    def process(
        self, parameters: NumeroParameters
    ) -> ReturnSuccessOrError[int | Nil, TestError]:
        if parameters.numero == 0:
            return self.ok(NIL)
        return self.ok(parameters.numero)

    def on_unexpected(self, exception: Exception) -> TestError:
        return UnexpectedError(message=str(exception))


async def test_sucesso_direto() -> None:
    result = await DobroUsecase()(NumeroParameters(numero=21))
    assert assert_success(result) == 42


async def test_erro_de_negocio_via_fail() -> None:
    result = await DobroUsecase()(NumeroParameters(numero=-1))
    assert assert_failure(result) == ValidationError(
        message='negativo', field='numero'
    )


async def test_paridade_direto_background_no_sucesso() -> None:
    params = NumeroParameters(numero=10)
    direto = await DobroUsecase()(params)
    background = await DobroUsecase(run_in_background=True)(params)
    assert direto == background


async def test_paridade_direto_background_no_erro_de_negocio() -> None:
    params = NumeroParameters(numero=-5)
    direto = await DobroUsecase()(params)
    background = await DobroUsecase(run_in_background=True)(params)
    assert direto == background


async def test_excecao_inesperada_vira_on_unexpected_direto() -> None:
    usecase = DobroUsecase(excecao=RuntimeError('bug'))
    result = await usecase(NumeroParameters(numero=1))
    assert assert_failure(result) == UnexpectedError(message='bug')


async def test_excecao_inesperada_vira_on_unexpected_background() -> None:
    usecase = DobroUsecase(
        run_in_background=True, excecao=RuntimeError('bug')
    )
    result = await usecase(NumeroParameters(numero=1))
    assert assert_failure(result) == UnexpectedError(message='bug')


@pytest.mark.parametrize('background', [False, True])
async def test_cancelamento_pendente_impede_o_process(
    background: bool,
) -> None:
    usecase = DobroUsecase(run_in_background=background)
    task = asyncio.create_task(usecase(NumeroParameters(numero=1)))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert usecase.process_chamado is False


@pytest.mark.parametrize('background', [False, True])
async def test_cancelled_error_do_process_propaga(
    background: bool,
) -> None:
    """CancelledError cooperativo não é engolido pelo on_unexpected."""
    usecase = DobroUsecase(
        run_in_background=background, excecao=asyncio.CancelledError()
    )
    with pytest.raises(asyncio.CancelledError):
        await usecase(NumeroParameters(numero=1))


async def test_monitor_nao_altera_o_resultado() -> None:
    result = await DobroUsecase(monitor_execution_time=True)(
        NumeroParameters(numero=21)
    )
    assert assert_success(result) == 42


async def test_monitor_chama_o_hook() -> None:
    usecase = DobroUsecase(monitor_execution_time=True)
    await usecase(NumeroParameters(numero=1))
    assert usecase.tempo_medido is not None
    assert usecase.tempo_medido >= timedelta(0)


async def test_monitor_desligado_nao_chama_o_hook() -> None:
    usecase = DobroUsecase()
    await usecase(NumeroParameters(numero=1))
    assert usecase.tempo_medido is None


async def test_hook_padrao_loga_em_debug() -> None:
    """A implementação padrão do hook não exige override."""

    class SemOverride(UsecaseBase[int, NumeroParameters, TestError]):
        def process(
            self, parameters: NumeroParameters
        ) -> ReturnSuccessOrError[int, TestError]:
            return self.ok(1)

        def on_unexpected(self, exception: Exception) -> TestError:
            return UnexpectedError(message=str(exception))

    result = await SemOverride(monitor_execution_time=True)(
        NumeroParameters(numero=1)
    )
    assert assert_success(result) == 1


async def test_resultado_unit() -> None:
    result = await VoidUsecase()(NumeroParameters(numero=1))
    assert assert_success(result) is UNIT


async def test_resultado_nil() -> None:
    encontrado = await BuscaOpcionalUsecase()(NumeroParameters(numero=7))
    vazio = await BuscaOpcionalUsecase()(NumeroParameters(numero=0))
    assert assert_success(encontrado) == 7
    assert assert_success(vazio) is NIL


async def test_dispatch_to_background_e_sobrescrevivel() -> None:
    """O despacho de background é um ponto de extensão (executor
    customizado — ex.: InterpreterPoolExecutor no 3.14+)."""
    from collections.abc import Callable
    from concurrent.futures import ThreadPoolExecutor

    class ExecutorCustomizado(DobroUsecase):
        def __init__(self) -> None:
            super().__init__(run_in_background=True)
            self.dispatch_usado = False

        async def _dispatch_to_background(
            self,
            run: Callable[[], ReturnSuccessOrError[int, TestError]],
        ) -> ReturnSuccessOrError[int, TestError]:
            self.dispatch_usado = True
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                return await loop.run_in_executor(executor, run)

    usecase = ExecutorCustomizado()
    result = await usecase(NumeroParameters(numero=21))
    assert assert_success(result) == 42
    assert usecase.dispatch_usado is True


async def test_dispatch_nao_e_usado_no_modo_direto() -> None:
    from collections.abc import Callable

    class EspiaoDispatch(DobroUsecase):
        def __init__(self) -> None:
            super().__init__(run_in_background=False)
            self.dispatch_usado = False

        async def _dispatch_to_background(
            self,
            run: Callable[[], ReturnSuccessOrError[int, TestError]],
        ) -> ReturnSuccessOrError[int, TestError]:
            self.dispatch_usado = True
            return run()

    usecase = EspiaoDispatch()
    await usecase(NumeroParameters(numero=1))
    assert usecase.dispatch_usado is False
