"""Representa uma operação concluída **sem valor de retorno**.

O análogo do ``Unit`` do C#: como ``None`` não distingue "sem valor" de
"valor ausente por erro", usa-se ``Unit`` como ``TValue`` quando o caso de
uso não produz dado algum — ``ReturnSuccessOrError[Unit, MeuErro]``.
"""

from typing import ClassVar, Final, final


@final
class Unit:
    """Singleton selado que representa "operação sem valor de retorno".

    Use a constante de módulo :data:`UNIT` (``Unit()`` também devolve
    sempre a mesma instância).
    """

    __slots__ = ()
    _instance: ClassVar['Unit | None'] = None

    def __new__(cls) -> 'Unit':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __reduce__(self) -> str:
        return 'UNIT'

    def __str__(self) -> str:
        return 'Unit - void'


UNIT: Final[Unit] = Unit()
"""Instância única de :class:`Unit`."""
