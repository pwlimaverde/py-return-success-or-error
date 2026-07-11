"""API pública da feature SalesReport.

O consumidor importa daqui — contrato do service, modelo, erros e a
função de registro — sem conhecer a estrutura interna de camadas.
"""

from features.sales_report.domain.errors import (
    BaseIndisponivel,
    SalesReportError,
    SemVendas,
)
from features.sales_report.domain.models import SalesReport
from features.sales_report.domain.services import SalesReportService
from features.sales_report.register import add_sales_report_feature

__all__ = [
    'BaseIndisponivel',
    'SalesReport',
    'SalesReportError',
    'SalesReportService',
    'SemVendas',
    'add_sales_report_feature',
]
