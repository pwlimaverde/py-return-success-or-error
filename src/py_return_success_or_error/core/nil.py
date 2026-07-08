"""Representa o **nulo como resultado válido e esperado**.

O análogo do ``Nil`` do C#: quando "não encontrado" é um sucesso legítimo
(e não uma falha), use ``Nil`` no valor — por exemplo
``ReturnSuccessOrError[Cliente | Nil, MeuErro]`` — em vez de ``None``,
que ficaria ambíguo, ou de um caso de erro, que forçaria o chamador a
tratar um não-erro como falha.
"""

from typing import ClassVar, Final, final


@final
class Nil:
    """Singleton selado que representa "nulo como resultado válido".

    Use a constante de módulo :data:`NIL` (``Nil()`` também devolve
    sempre a mesma instância).
    """

    __slots__ = ()
    _instance: ClassVar['Nil | None'] = None

    def __new__(cls) -> 'Nil':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __reduce__(self) -> str:
        return 'NIL'

    def __str__(self) -> str:
        return 'Nil - null'


NIL: Final[Nil] = Nil()
"""Instância única de :class:`Nil`."""
