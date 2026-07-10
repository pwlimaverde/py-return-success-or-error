"""Fonte em memória.

A dupla InMemory/Csv demonstra a **portabilidade**: o repositório e o
caso de uso não mudam uma linha quando a fonte troca.
"""

import asyncio

from py_return_success_or_error import DataSource

from features.sales_report.domain.models import SalesRows
from features.sales_report.domain.parameters import SalesReportParameters


class InMemorySalesDataSource(
    DataSource[SalesRows, SalesReportParameters]
):
    """Fonte em memória."""

    def __init__(self, rows: SalesRows) -> None:
        self._rows = rows

    async def __call__(
        self, parameters: SalesReportParameters
    ) -> SalesRows:
        await asyncio.sleep(0)  # simula I/O
        return list(self._rows)
