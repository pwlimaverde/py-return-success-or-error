"""Contrato do service da feature."""

from abc import ABC, abstractmethod

from py_return_success_or_error import ReturnSuccessOrError

from features.fibonacci.domain.errors import FibonacciError


class FibonacciService(ABC):
    """Ponto de entrada público da feature — o que a UI consome."""

    @abstractmethod
    async def calcular(
        self, posicao: int
    ) -> ReturnSuccessOrError[int, FibonacciError]:
        """Calcula o n-ésimo número de Fibonacci."""
