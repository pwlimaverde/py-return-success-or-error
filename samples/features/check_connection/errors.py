"""União fechada de erros da feature CheckConnection."""

from dataclasses import dataclass

from py_return_success_or_error import AppError, ErrorGeneric


@dataclass(frozen=True)
class Offline(AppError):
    """Sem conectividade."""


@dataclass(frozen=True)
class ConnectionTimeout(AppError):
    """A verificação excedeu o tempo limite."""


type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric
