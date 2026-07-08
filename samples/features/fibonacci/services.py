"""Service facade da feature Fibonacci."""

from py_return_success_or_error import ReturnSuccessOrError

from features.fibonacci.errors import FibonacciError
from features.fibonacci.usecases import FibonacciParameters, FibonacciUsecase


class FibonacciService:
    """Fachada fina sobre o caso de uso."""

    def __init__(self, usecase: FibonacciUsecase) -> None:
        self._usecase = usecase

    async def calcular(
        self, posicao: int
    ) -> ReturnSuccessOrError[int, FibonacciError]:
        return await self._usecase(FibonacciParameters(posicao=posicao))
