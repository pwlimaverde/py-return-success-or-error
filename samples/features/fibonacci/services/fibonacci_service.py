"""Implementação do contrato do service."""

from py_return_success_or_error import ReturnSuccessOrError

from features.fibonacci.domain.errors import FibonacciError
from features.fibonacci.domain.parameters import FibonacciParameters
from features.fibonacci.domain.services import FibonacciService
from features.fibonacci.domain.usecases import FibonacciUsecase


class FibonacciServiceImpl(FibonacciService):
    """Fachada fina sobre o caso de uso."""

    def __init__(self, usecase: FibonacciUsecase) -> None:
        self._usecase = usecase

    async def calcular(
        self, posicao: int
    ) -> ReturnSuccessOrError[int, FibonacciError]:
        return await self._usecase(FibonacciParameters(posicao=posicao))
