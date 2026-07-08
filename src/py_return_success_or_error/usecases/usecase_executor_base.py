"""Base compartilhada pelos casos de uso (≙ UsecaseExecutorBase.cs)."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from datetime import timedelta

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
)

_logger = logging.getLogger('py_return_success_or_error')


class UsecaseExecutorBase[TValue, TError](ABC):
    """Base compartilhada pelos casos de uso.

    Concentra o que é comum aos dois fluxos (:class:`UsecaseBase` e
    :class:`UsecaseBaseCallData`): a medição opcional do tempo e o
    despacho opcional do processamento (CPU-bound) a uma thread. As
    subclasses definem o fluxo específico e implementam o ``process``.

    Attributes:
        run_in_background: Se verdadeiro, o ``process`` (CPU-bound) roda
            fora do event loop via :meth:`_dispatch_to_background`
            (padrão: ``asyncio.to_thread``, análogo do ``Task.Run``),
            mantendo o loop responsivo. No build padrão do CPython o
            GIL limita o paralelismo de CPU puro (no free-threaded,
            3.14+, o paralelismo é real); uma thread já iniciada não é
            interrompida pelo cancelamento da task.
        monitor_execution_time: Se verdadeiro, mede o tempo de execução
            e o entrega a :meth:`on_execution_time_measured`.
    """

    def __init__(
        self,
        *,
        run_in_background: bool = False,
        monitor_execution_time: bool = False,
    ) -> None:
        """Configura as flags de execução do caso de uso.

        Args:
            run_in_background: Despacha o ``process`` para uma thread.
            monitor_execution_time: Habilita a medição de tempo.
        """
        self.run_in_background = run_in_background
        self.monitor_execution_time = monitor_execution_time

    @abstractmethod
    def on_unexpected(self, exception: Exception) -> TError:
        """Converte uma exceção **inesperada** do ``process`` (um bug)
        num erro do conjunto fechado da feature.

        **Abstrato**: como não há erro universal a fabricar, o caso de
        uso decide para qual caso de ``TError`` o inesperado é mapeado
        (tipicamente um caso "Unexpected"/``ErrorGeneric``). Garante que
        o ``process`` nunca lança ao chamador — o resultado é sempre um
        dos casos previstos.

        **Exceção do contrato — cancelamento**: um
        ``asyncio.CancelledError`` não passa por aqui: cancelamento não é
        falha de domínio e propaga como exceção, no idioma do asyncio.

        Args:
            exception: A exceção inesperada capturada.

        Returns:
            O erro de domínio correspondente.
        """
        ...  # pragma: no cover

    def on_execution_time_measured(self, elapsed: timedelta) -> None:
        """Recebe o tempo medido quando ``monitor_execution_time`` está
        habilitado.

        **Virtual**: sobrescreva para integrar à sua observabilidade —
        a base não impõe dependência de logging. A implementação padrão
        registra em ``logging`` no nível DEBUG (logger
        ``py_return_success_or_error``), o análogo do ``Trace.WriteLine``
        do C#.

        Args:
            elapsed: Duração total da execução do caso de uso.
        """
        modo = 'Background' if self.run_in_background else 'Direct'
        _logger.debug(
            '[py-return-success-or-error] Execution Time %s (%s): %.2fms',
            type(self).__name__,
            modo,
            elapsed.total_seconds() * 1000,
        )

    def ok(self, value: TValue) -> ReturnSuccessOrError[TValue, TError]:
        """Cria um resultado de **sucesso** a partir do valor.

        Conveniência simétrica a :meth:`fail` — como Python não tem as
        conversões implícitas do C#, ``self.ok(valor)`` é a forma
        recomendada de retornar sucesso dentro do ``process``.

        Args:
            value: O valor de sucesso.

        Returns:
            ``Success(value)`` tipado com os parâmetros do caso de uso.
        """
        return Success(value)

    def fail(self, error: TError) -> ReturnSuccessOrError[TValue, TError]:
        """Cria um resultado de **falha** a partir de um caso concreto do
        conjunto fechado de erro.

        É a forma recomendada de retornar um erro de negócio no
        ``process`` (≙ ``Fail`` do C#, que resolve o "duplo salto" de
        conversões implícitas — aqui, resolve a inferência de tipos).

        Args:
            error: Um caso concreto de ``TError``.

        Returns:
            ``Failure(error)`` tipado com os parâmetros do caso de uso.
        """
        return Failure(error)

    async def _measured(
        self,
        run: Callable[[], Awaitable[ReturnSuccessOrError[TValue, TError]]],
    ) -> ReturnSuccessOrError[TValue, TError]:
        """Envolve a execução com a medição de tempo, quando habilitada."""
        if not self.monitor_execution_time:
            return await run()

        start = time.perf_counter()
        result = await run()
        elapsed = timedelta(seconds=time.perf_counter() - start)
        self.on_execution_time_measured(elapsed)
        return result

    async def _dispatch_to_background(
        self,
        run: Callable[[], ReturnSuccessOrError[TValue, TError]],
    ) -> ReturnSuccessOrError[TValue, TError]:
        """Despacha o processamento quando ``run_in_background`` está
        habilitado.

        **Virtual**: o padrão é ``asyncio.to_thread`` (≙ ``Task.Run``),
        que mantém o event loop responsivo. No CPython **free-threaded**
        (3.14+, PEP 779) isso já dá paralelismo real de CPU; no build
        padrão, o GIL limita o paralelismo de CPU puro — sobrescreva
        para usar outro executor quando precisar, por exemplo o
        ``InterpreterPoolExecutor`` do Python 3.14+ (PEP 734)::

            async def _dispatch_to_background(self, run):
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(self._executor, run)

        Args:
            run: O processamento já protegido (nunca lança, exceto
                cancelamento).

        Returns:
            O resultado do processamento.
        """
        return await asyncio.to_thread(run)

    async def _process_stage(
        self,
        process: Callable[[], ReturnSuccessOrError[TValue, TError]],
    ) -> ReturnSuccessOrError[TValue, TError]:
        """Executa o ``process`` direto ou, se ``run_in_background``,
        via :meth:`_dispatch_to_background`.

        Em **ambos** os modos, uma exceção inesperada é convertida via
        :meth:`on_unexpected` em ``Failure`` — o ``process`` nunca
        propaga exceção ao chamador. Única exceção: o **cancelamento**
        (``asyncio.CancelledError``) propaga em ambos os modos —
        cancelamento não é falha de domínio.
        """
        # Paridade direto↔background: um cancelamento já pendente é
        # entregue ANTES do process, nos dois modos (análogo do
        # ThrowIfCancellationRequested do C#).
        await asyncio.sleep(0)

        def guarded() -> ReturnSuccessOrError[TValue, TError]:
            try:
                return process()
            except asyncio.CancelledError:
                raise
            except Exception as exception:
                return Failure(self.on_unexpected(exception))

        if not self.run_in_background:
            return guarded()

        return await self._dispatch_to_background(guarded)
