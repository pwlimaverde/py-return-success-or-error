"""Implementação do contrato do service."""

from py_return_success_or_error import ReturnSuccessOrError

from features.sales_report.domain.errors import SalesReportError
from features.sales_report.domain.models import SalesReport
from features.sales_report.domain.parameters import SalesReportParameters
from features.sales_report.domain.services import SalesReportService
from features.sales_report.domain.usecases import GenerateSalesReportUsecase


class SalesReportServiceImpl(SalesReportService):
    """Fachada fina sobre o caso de uso."""

    def __init__(self, usecase: GenerateSalesReportUsecase) -> None:
        self._usecase = usecase

    async def gerar(
        self, valor_minimo: float
    ) -> ReturnSuccessOrError[SalesReport, SalesReportError]:
        return await self._usecase(
            SalesReportParameters(valor_minimo=valor_minimo)
        )
