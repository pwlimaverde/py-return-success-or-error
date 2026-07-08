"""Portas de dados da feature SalesReport — duas implementações.

A dupla InMemory/Csv demonstra a **portabilidade**: o repositório e o
caso de uso não mudam uma linha quando a fonte troca.
"""

import asyncio
from dataclasses import dataclass

from py_return_success_or_error import DataSource, Parameters


@dataclass(frozen=True)
class SalesReportParameters(Parameters):
    valor_minimo: float


type SalesRows = list[tuple[str, float]]
"""Linhas brutas de venda: (produto, valor)."""


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


class CsvSalesDataSource(DataSource[SalesRows, SalesReportParameters]):
    """Fonte CSV (conteúdo em string para o sample ser autocontido)."""

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
