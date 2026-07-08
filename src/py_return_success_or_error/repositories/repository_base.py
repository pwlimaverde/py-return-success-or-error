"""Implementação base do repositório — a fronteira try/except."""

import asyncio
from abc import abstractmethod

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
)
from py_return_success_or_error.datasources.datasource import DataSource
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.repositories.repository import Repository


class RepositoryBase[TData, TParams: Parameters, TError](
    Repository[TData, TParams, TError]
):
    """Camada anticorrupção sobre um :class:`DataSource`.

    Envolve a chamada ao datasource numa fronteira try/except (o análogo
    do ``RepositoryBase.CallAsync`` do C#):

    - sucesso → ``Success[TData]``;
    - exceção técnica → :meth:`map_error` → ``Failure[TError]``;
    - ``asyncio.CancelledError`` → **propaga** (cancelamento não é falha
      de domínio).
    """

    def __init__(self, datasource: DataSource[TData, TParams]) -> None:
        """Inicializa com a porta de dados a proteger.

        Args:
            datasource: A porta "burra" de acesso ao recurso externo.
        """
        self._datasource = datasource

    async def __call__(
        self, parameters: TParams
    ) -> ReturnSuccessOrError[TData, TError]:
        """Executa o datasource dentro da fronteira de erro.

        Args:
            parameters: Parâmetros da busca.

        Returns:
            ``Success`` com o dado bruto, ou ``Failure`` com o erro
            traduzido por :meth:`map_error`.
        """
        try:
            return Success(await self._datasource(parameters))
        except asyncio.CancelledError:
            raise
        except Exception as exception:
            return Failure(self.map_error(exception, parameters))

    @abstractmethod
    def map_error(self, exception: Exception, parameters: TParams) -> TError:
        """Traduz a exceção técnica num caso do conjunto fechado da feature.

        **Abstrato**: não há erro universal a fabricar — cada repositório
        decide como cada exceção vira um caso de ``TError`` (tipicamente
        com um caso "genérico" para o inesperado).

        Args:
            exception: A exceção técnica capturada.
            parameters: Os parâmetros da chamada que falhou.

        Returns:
            O erro de domínio correspondente.
        """
        ...  # pragma: no cover
