"""Camada anticorrupção da feature SalesReport."""

from py_return_success_or_error import ErrorGeneric, RepositoryBase

from features.sales_report.datasources import SalesReportParameters, SalesRows
from features.sales_report.errors import BaseIndisponivel, SalesReportError


class SalesReportRepository(
    RepositoryBase[SalesRows, SalesReportParameters, SalesReportError]
):
    """Traduz falhas técnicas da fonte de vendas em erros da feature."""

    def map_error(
        self, exception: Exception, parameters: SalesReportParameters
    ) -> SalesReportError:
        match exception:
            case OSError() | ValueError():
                return BaseIndisponivel(message=str(exception))
            case _:
                return ErrorGeneric(message=str(exception))
