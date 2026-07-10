"""Fonte CSV.

Conteúdo em string para o sample ser autocontido.
"""

import asyncio

from py_return_success_or_error import DataSource

from features.sales_report.domain.models import SalesRows
from features.sales_report.domain.parameters import SalesReportParameters


class CsvSalesDataSource(DataSource[SalesRows, SalesReportParameters]):
    """Fonte CSV."""

    def __init__(self, conteudo_csv: str) -> None:
        self._conteudo_csv = conteudo_csv

    async def __call__(
        self, parameters: SalesReportParameters
    ) -> SalesRows:
        await asyncio.sleep(0)  # simula I/O
        rows: SalesRows = []
        for linha in self._conteudo_csv.strip().splitlines():
            produto, valor = linha.split(';')
            rows.append((produto, float(valor)))
        return rows
