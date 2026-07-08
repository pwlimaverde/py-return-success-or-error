"""Base opcional para os erros de domínio da aplicação."""

from abc import ABC
from dataclasses import dataclass, replace
from typing import Self


@dataclass(frozen=True)
class AppError(ABC):
    """Base abstrata para erros de domínio, modelados como **valores**.

    Diferente de exceções, um ``AppError`` é imutável, tem igualdade por
    valor e trafega dentro de ``Failure`` — nunca é lançado. Cada feature
    declara os seus casos concretos herdando desta base e os agrupa numa
    união fechada::

        @dataclass(frozen=True)
        class Offline(AppError):
            ...

        @dataclass(frozen=True)
        class ConnectionTimeout(AppError):
            ...

        type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric

    Herdar de ``AppError`` é **conveniência, não obrigação**: ``TError``
    pode ser qualquer tipo. A base só fornece ``message``, igualdade por
    valor e :meth:`with_message`.

    Attributes:
        message: Descrição do erro.
    """

    message: str

    def __post_init__(self) -> None:
        if type(self) is AppError:
            raise TypeError(
                'AppError é abstrata; declare um caso concreto da feature.'
            )

    def with_message(self, message: str) -> Self:
        """Devolve uma **nova** instância com ``message`` substituída.

        Preserva o tipo concreto e os demais campos — o análogo do
        ``this with { Message = message }`` do C#.

        Args:
            message: A nova mensagem.

        Returns:
            Nova instância do mesmo tipo concreto.
        """
        return replace(self, message=message)
