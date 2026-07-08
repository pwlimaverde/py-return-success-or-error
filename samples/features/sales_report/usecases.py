"""Caso de uso da feature SalesReport."""

from dataclasses import dataclass

from py_return_success_or_error import (
    ErrorGeneric,
    Repository,
    ReturnSuccessOrError,
    UsecaseBaseCallData,
)

from features.sales_report.datasources import SalesReportParameters, SalesRows
from features.sales_report.errors import SalesReportError, SemVendas


@dataclass(frozen=True)
class SalesReport:
    """Relatório consolidado de vendas."""

    total: float
    quantidade: int
    ticket_medio: float


class GenerateSalesReportUsecase(
    UsecaseBaseCallData[
        SalesReport, SalesRows, SalesReportParameters, SalesReportError
    ]
):
    """Consolida as vendas acima do valor mínimo num relatório."""

    def __init__(
        self,
        repository: Repository[
            SalesRows, SalesReportParameters, SalesReportError
        ],
        *,
        run_in_background: bool = False,
        monitor_execution_time: bool = False,
    ) -> None:
        super().__init__(
            repository,
            run_in_background=run_in_background,
            monitor_execution_time=monitor_execution_time,
        )

    def process(
        self, data: SalesRows, parameters: SalesReportParameters
    ) -> ReturnSuccessOrError[SalesReport, SalesReportError]:
        filtradas = [
            valor
            for _, valor in data
            if valor >= parameters.valor_minimo
        ]
        if not filtradas:
            return self.fail(
                SemVendas(
                    message=(
                        'nenhuma venda acima de '
                        f'{parameters.valor_minimo:.2f}'
                    )
                )
            )
        total = sum(filtradas)
        return self.ok(
            SalesReport(
                total=total,
                quantidade=len(filtradas),
                ticket_medio=total / len(filtradas),
            )
        )

    def on_unexpected(self, exception: Exception) -> SalesReportError:
        return ErrorGeneric(message=str(exception))
