"""Erro genérico pronto para o caso "inesperado"."""

from dataclasses import dataclass
from typing import final

from py_return_success_or_error.errors.app_error import AppError


@final
@dataclass(frozen=True)
class ErrorGeneric(AppError):
    """Caso de erro pronto para falhas **inesperadas** (bugs, exceções).

    Inclua-o na união fechada da feature como o "caso catch-all" e
    devolva-o em ``on_unexpected``/``map_error`` quando não houver caso
    mais específico::

        type MinhaFeatureError = RegraVioladaError | ErrorGeneric
    """

    def __str__(self) -> str:
        return f'ErrorGeneric - {self.message}'
