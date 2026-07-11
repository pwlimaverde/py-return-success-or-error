"""Contrato base dos parâmetros de entrada das camadas."""

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Parameters(ABC):
    """Base abstrata dos parâmetros de entrada — **só dados**.

    Diferente da versão 0.x, os parâmetros não carregam erro de fallback:
    o tratamento de erro pertence a cada camada (``map_error`` no
    repositório, ``on_unexpected`` no caso de uso). Declare os campos da
    feature num dataclass congelado::

        @dataclass(frozen=True)
        class BuscaClienteParameters(Parameters):
            cliente_id: int
    """

    def __post_init__(self) -> None:
        if type(self) is Parameters:
            raise TypeError(
                'Parameters é abstrata; declare os parâmetros da feature.'
            )
