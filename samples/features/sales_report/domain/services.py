"""Contrato do service da feature."""

from abc import ABC, abstractmethod

from py_return_success_or_error import ReturnSuccessOrError

from features.sales_report.domain.errors import SalesReportError
from features.sales_report.domain.models import SalesReport


class SalesReportService(ABC):
    """Ponto de entrada público da feature — o que a UI consome."""

    @abstractmethod
    async def gerar(
        self, valor_minimo: float
    ) -> ReturnSuccessOrError[SalesReport, SalesReportError]:
        """Consolida as vendas acima do valor mínimo num relatório."""
