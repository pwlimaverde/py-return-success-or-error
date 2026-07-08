"""O tipo de resultado da biblioteca: uma união fechada de sucesso ou falha.

``ReturnSuccessOrError[TValue, TError]`` é um alias de união de
:class:`Success` e :class:`Failure` — o análogo Python do ``union`` nativo
do C#. O erro é **parametrizado por feature**: cada caso de uso declara o
seu conjunto fechado de erros (tipicamente uma união de tipos concretos),
e o consumidor trata todos os casos de forma exaustiva.

Consumo canônico (exaustivo, provado pelo mypy/pyright)::

    match result:
        case Success(value):
            ...  # caminho feliz
        case Failure(error):
            ...  # trate cada caso do union de erro
        case _:
            assert_never(result)

Para o estilo funcional, use a função :func:`match` — o equivalente ao
``Match`` do C#.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import assert_never, final


@final
@dataclass(frozen=True, slots=True)
class Success[TValue]:
    """Caso de **sucesso** do resultado, carregando o valor produzido.

    Imutável e com igualdade por valor, como o ``record Success<TValue>``
    do C#.

    Attributes:
        value: O valor de sucesso.
    """

    value: TValue

    def __str__(self) -> str:
        return f'Success: {self.value}'


@final
@dataclass(frozen=True, slots=True)
class Failure[TError]:
    """Caso de **falha** do resultado, carregando o erro ocorrido.

    Imutável e com igualdade por valor, como o ``record Failure<TError>``
    do C#. ``TError`` é o conjunto fechado de erros da feature — não há
    erro universal imposto pela biblioteca.

    Attributes:
        error: O erro da feature.
    """

    error: TError

    def __str__(self) -> str:
        return f'Failure: {self.error}'


type ReturnSuccessOrError[TValue, TError] = (
    Success[TValue] | Failure[TError]
)
"""União fechada de :class:`Success` e :class:`Failure`.

O análogo do ``union ReturnSuccessOrError<TValue, TError>`` do C#: só
existem dois casos, e o ``match/case`` com ``assert_never`` prova a
cobertura de ambos em tempo de checagem de tipos.
"""


def match[TValue, TError, TResult](
    result: ReturnSuccessOrError[TValue, TError],
    *,
    on_success: Callable[[TValue], TResult],
    on_error: Callable[[TError], TResult],
) -> TResult:
    """Consome o resultado de forma exaustiva, no estilo funcional.

    Equivalente ao ``Match(onSuccess, onError)`` do C#: exatamente um dos
    dois ramos é executado e o seu retorno é devolvido.

    Args:
        result: O resultado a consumir.
        on_success: Ramo executado com o valor quando for :class:`Success`.
        on_error: Ramo executado com o erro quando for :class:`Failure`.

    Returns:
        O retorno do ramo executado.
    """
    match result:
        case Success(value):
            return on_success(value)
        case Failure(error):
            return on_error(error)
        case _:  # pragma: no cover - inalcançável, provado pelo mypy
            assert_never(result)
