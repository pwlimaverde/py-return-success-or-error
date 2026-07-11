"""Contrato da camada de repositório."""

from abc import ABC, abstractmethod

from py_return_success_or_error.core.return_success_or_error import (
    ReturnSuccessOrError,
)
from py_return_success_or_error.parameters.parameters import Parameters


class Repository[TData, TParams: Parameters, TError](ABC):
    """Contrato do repositório: nunca lança falha técnica ao chamador.

    É a abstração que o caso de uso recebe (inversão de dependência):
    devolve sempre ``Success[TData]`` ou ``Failure[TError]``, com o erro
    já traduzido para o conjunto fechado da feature.
    """

    @abstractmethod
    async def __call__(
        self, parameters: TParams
    ) -> ReturnSuccessOrError[TData, TError]:
        """Busca o dado e traduz falhas técnicas em erro de domínio.

        Args:
            parameters: Parâmetros da busca.

        Returns:
            ``Success`` com o dado, ou ``Failure`` com o erro da feature.
        """
        ...  # pragma: no cover
