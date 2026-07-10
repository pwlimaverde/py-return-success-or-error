"""Caso de uso de lógica pura, sem acesso a dados."""

from abc import abstractmethod

from py_return_success_or_error.core.return_success_or_error import (
    ReturnSuccessOrError,
)
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.usecases.usecase_executor_base import (
    UsecaseExecutorBase,
)


class UsecaseBase[TValue, TParams: Parameters, TError](
    UsecaseExecutorBase[TValue, TError]
):
    """Caso de uso de **lógica pura**: sem datasource/repositório.

    A subclasse implementa apenas :meth:`process` (síncrono, CPU-bound) e
    :meth:`on_unexpected`. O chamador invoca o caso de uso como uma
    função assíncrona::

        result = await usecase(parameters)
    """

    @abstractmethod
    def process(
        self, parameters: TParams
    ) -> ReturnSuccessOrError[TValue, TError]:
        """A regra de negócio da feature — **síncrona** e CPU-bound.

        Retorne com ``self.ok(valor)`` / ``self.fail(erro)``. Não deve
        fazer I/O: dados externos entram pelo fluxo
        :class:`UsecaseBaseCallData`.

        Args:
            parameters: Parâmetros de entrada da feature.

        Returns:
            ``Success`` ou ``Failure`` do conjunto fechado da feature.
        """
        ...  # pragma: no cover

    async def __call__(
        self, parameters: TParams
    ) -> ReturnSuccessOrError[TValue, TError]:
        """Orquestra a execução: medição opcional + despacho do process.

        Args:
            parameters: Parâmetros de entrada da feature.

        Returns:
            O resultado do ``process``, com o inesperado já convertido
            via ``on_unexpected``.
        """
        return await self._measured(
            lambda: self._process_stage(lambda: self.process(parameters))
        )
