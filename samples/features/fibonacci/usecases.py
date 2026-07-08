"""Caso de uso da feature Fibonacci — lógica pura, CPU-bound."""

from dataclasses import dataclass

from py_return_success_or_error import (
    ErrorGeneric,
    Parameters,
    ReturnSuccessOrError,
    UsecaseBase,
)

from features.fibonacci.errors import EntradaInvalida, FibonacciError


@dataclass(frozen=True)
class FibonacciParameters(Parameters):
    posicao: int


class FibonacciUsecase(
    UsecaseBase[int, FibonacciParameters, FibonacciError]
):
    """Calcula o n-ésimo número de Fibonacci.

    CPU-bound puro: o sample o registra com ``run_in_background=True`` e
    ``monitor_execution_time=True`` para demonstrar o despacho a thread e
    a medição de tempo.
    """

    def process(
        self, parameters: FibonacciParameters
    ) -> ReturnSuccessOrError[int, FibonacciError]:
        if parameters.posicao < 0:
            return self.fail(
                EntradaInvalida(
                    message='posição deve ser >= 0',
                    posicao=parameters.posicao,
                )
            )
        a, b = 0, 1
        for _ in range(parameters.posicao):
            a, b = b, a + b
        return self.ok(a)

    def on_unexpected(self, exception: Exception) -> FibonacciError:
        return ErrorGeneric(message=str(exception))
