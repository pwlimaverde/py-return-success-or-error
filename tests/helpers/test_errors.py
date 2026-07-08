"""União fechada de erros reutilizada pelos testes (≙ TestErrors.cs)."""

from dataclasses import dataclass
from typing import assert_never

from py_return_success_or_error.errors.app_error import AppError


@dataclass(frozen=True)
class NotFoundError(AppError):
    """Recurso não encontrado."""


@dataclass(frozen=True)
class ValidationError(AppError):
    """Entrada inválida."""

    field: str = ''


@dataclass(frozen=True)
class UnexpectedError(AppError):
    """Falha inesperada (bug)."""


type TestError = NotFoundError | ValidationError | UnexpectedError


def text(error: TestError) -> str:
    """Consumo exaustivo da união — a cobertura é provada pelo mypy."""
    match error:
        case NotFoundError():
            return f'não encontrado: {error.message}'
        case ValidationError():
            return f'inválido[{error.field}]: {error.message}'
        case UnexpectedError():
            return f'inesperado: {error.message}'
        case _:
            assert_never(error)
