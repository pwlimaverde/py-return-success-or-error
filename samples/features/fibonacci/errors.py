"""União fechada de erros da feature Fibonacci."""

from dataclasses import dataclass

from py_return_success_or_error import AppError, ErrorGeneric


@dataclass(frozen=True)
class EntradaInvalida(AppError):
    """A posição pedida não é válida."""

    posicao: int = 0


type FibonacciError = EntradaInvalida | ErrorGeneric
