"""Registro da feature SalesReport (≙ AddSalesReportFeature).

Para trocar a fonte, basta trocar a fábrica do datasource — repositório,
caso de uso e service não mudam (portabilidade).
"""

from composition.container import Container
from features.sales_report.datasources import (
    CsvSalesDataSource,
    InMemorySalesDataSource,
)
from features.sales_report.repositories import SalesReportRepository
from features.sales_report.services import SalesReportService
from features.sales_report.usecases import GenerateSalesReportUsecase

_CSV = """
Notebook;4200.00
Mouse;89.90
Teclado;250.00
Monitor;1600.00
Cabo HDMI;35.00
"""


def add_sales_report_feature(container: Container) -> Container:
    """Registra todas as camadas da feature no container."""
    return (
        container.add_singleton(
            CsvSalesDataSource, lambda _: CsvSalesDataSource(_CSV)
        )
        .add_singleton(
            InMemorySalesDataSource,
            lambda _: InMemorySalesDataSource(
                [('Notebook', 4200.0), ('Mouse', 89.9)]
            ),
        )
        .add_singleton(
            SalesReportRepository,
            # troque para c.resolve(InMemorySalesDataSource) e nada mais muda
            lambda c: SalesReportRepository(
                c.resolve(CsvSalesDataSource)
            ),
        )
        .add_singleton(
            GenerateSalesReportUsecase,
            lambda c: GenerateSalesReportUsecase(
                c.resolve(SalesReportRepository),
                run_in_background=True,
                monitor_execution_time=True,
            ),
        )
        .add_singleton(
            SalesReportService,
            lambda c: SalesReportService(
                c.resolve(GenerateSalesReportUsecase)
            ),
        )
    )
