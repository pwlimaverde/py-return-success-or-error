"""Porta "burra" de acesso a dados externos."""

from abc import ABC, abstractmethod

from py_return_success_or_error.parameters.parameters import Parameters


class DataSource[TData, TParams: Parameters](ABC):
    """Porta de acesso a um recurso externo (HTTP, banco, arquivo...).

    Contrato deliberadamente "burro": devolve o dado **bruto** ou
    **lança** a exceção técnica original (``TimeoutError``, ``OSError``,
    erro do driver...). Não conhece o domínio nem o modelo de erro da
    feature — a tradução exceção→erro é responsabilidade do
    :class:`~py_return_success_or_error.repositories.repository_base.RepositoryBase`.

    O cancelamento asyncio é ambiente: um ``asyncio.CancelledError`` pode
    emergir de qualquer ``await`` interno e deve propagar.
    """

    @abstractmethod
    async def __call__(self, parameters: TParams) -> TData:
        """Executa a chamada externa.

        Args:
            parameters: Parâmetros da chamada.

        Returns:
            O dado bruto obtido.

        Raises:
            Exception: Qualquer falha técnica da infraestrutura.
        """
        ...  # pragma: no cover
