"""Caso de uso com busca de dados."""

from abc import abstractmethod
from typing import assert_never

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
)
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.repositories.repository import Repository
from py_return_success_or_error.usecases.usecase_executor_base import (
    UsecaseExecutorBase,
)


class UsecaseBaseCallData[TValue, TData, TParams: Parameters, TError](
    UsecaseExecutorBase[TValue, TError]
):
    """Caso de uso que **busca dados** antes de aplicar a regra.

    Depende da abstração :class:`Repository` (inversão de dependência) e
    orquestra três fases:

    1. **FETCH** — ``await repository(parameters)``;
    2. **CURTO-CIRCUITO** — um ``Failure`` do fetch retorna direto ao
       chamador, sem executar o ``process``;
    3. **PROCESS** — a regra de negócio recebe o dado limpo.
    """

    def __init__(
        self,
        repository: Repository[TData, TParams, TError],
        *,
        run_in_background: bool = False,
        monitor_execution_time: bool = False,
    ) -> None:
        """Inicializa com o repositório da feature.

        Args:
            repository: A abstração de acesso a dados da feature.
            run_in_background: Despacha o ``process`` para uma thread.
            monitor_execution_time: Habilita a medição de tempo.
        """
        super().__init__(
            run_in_background=run_in_background,
            monitor_execution_time=monitor_execution_time,
        )
        self._repository = repository

    @abstractmethod
    def process(
        self, data: TData, parameters: TParams
    ) -> ReturnSuccessOrError[TValue, TError]:
        """A regra de negócio da feature — **síncrona** e CPU-bound.

        Só é chamada quando o fetch teve sucesso: ``data`` chega limpo.
        Retorne com ``self.ok(valor)`` / ``self.fail(erro)``.

        Args:
            data: O dado obtido pelo repositório.
            parameters: Parâmetros de entrada da feature.

        Returns:
            ``Success`` ou ``Failure`` do conjunto fechado da feature.
        """
        ...  # pragma: no cover

    async def __call__(
        self, parameters: TParams
    ) -> ReturnSuccessOrError[TValue, TError]:
        """Orquestra FETCH → CURTO-CIRCUITO → PROCESS.

        Args:
            parameters: Parâmetros de entrada da feature.

        Returns:
            O ``Failure`` do fetch inalterado, ou o resultado do
            ``process`` com o inesperado já convertido.
        """

        async def run() -> ReturnSuccessOrError[TValue, TError]:
            fetch_result = await self._repository(parameters)
            match fetch_result:
                case Failure() as failure:
                    return failure
                case Success(data):
                    return await self._process_stage(
                        lambda: self.process(data, parameters)
                    )
                case _:  # pragma: no cover - provado pelo mypy
                    assert_never(fetch_result)

        return await self._measured(run)
