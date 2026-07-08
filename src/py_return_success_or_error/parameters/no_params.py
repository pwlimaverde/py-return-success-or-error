"""Parâmetro vazio para operações sem entrada."""

from dataclasses import dataclass
from typing import ClassVar, Final, final

from py_return_success_or_error.parameters.parameters import Parameters


@final
@dataclass(frozen=True)
class NoParams(Parameters):
    """Singleton que representa "operação sem parâmetros de entrada".

    Use a constante de módulo :data:`NO_PARAMS` (``NoParams()`` também
    devolve sempre a mesma instância).
    """

    _instance: ClassVar['NoParams | None'] = None

    def __new__(cls) -> 'NoParams':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __reduce__(self) -> str:
        return 'NO_PARAMS'


NO_PARAMS: Final[NoParams] = NoParams()
"""Instância única de :class:`NoParams`."""
