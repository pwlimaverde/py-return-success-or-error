"""Service facade da feature SalesReport."""

from py_return_success_or_error import ReturnSuccessOrError

from features.sales_report.datasources import SalesReportParameters
from features.sales_report.errors import SalesReportError
from features.sales_report.usecases import (
    GenerateSalesReportUsecase,
    SalesReport,
)


class SalesReportService:
    """Fachada fina sobre o caso de uso."""

    def __init__(self, usecase: GenerateSalesReportUsecase) -> None:
        self._usecase = usecase

    async def gerar(
        self, valor_minimo: float
    ) -> ReturnSuccessOrError[SalesReport, SalesReportError]:
        return await self._usecase(
            SalesReportParameters(valor_minimo=valor_minimo)
        )
