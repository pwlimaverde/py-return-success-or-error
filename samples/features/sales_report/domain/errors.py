"""União fechada de erros da feature."""

from dataclasses import dataclass

from py_return_success_or_error import AppError, ErrorGeneric


@dataclass(frozen=True)
class BaseIndisponivel(AppError):
    """A fonte de vendas não pôde ser lida."""


@dataclass(frozen=True)
class SemVendas(AppError):
    """Não há vendas no período pedido."""


type SalesReportError = BaseIndisponivel | SemVendas | ErrorGeneric
