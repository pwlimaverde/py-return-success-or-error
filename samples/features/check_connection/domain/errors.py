"""União fechada de erros da feature."""

from dataclasses import dataclass

from py_return_success_or_error import AppError, ErrorGeneric


@dataclass(frozen=True)
class Offline(AppError):
    """Erro de negócio: sem conectividade (decidido no ``process``)."""


@dataclass(frozen=True)
class ConnectionTimeout(AppError):
    """Falha de I/O traduzida pelo repository (timeout da fonte)."""


type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric
"""Os 3 erros possíveis desta feature — consumo exaustivo, sem ``_``."""
