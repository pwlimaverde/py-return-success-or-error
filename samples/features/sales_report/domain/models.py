"""Modelos do domínio da feature."""

from dataclasses import dataclass

type SalesRows = list[tuple[str, float]]
"""Linhas brutas de venda vindas da fonte: (produto, valor)."""


@dataclass(frozen=True)
class SalesReport:
    """Relatório consolidado de vendas (valor de sucesso do caso de uso)."""

    total: float
    quantidade: int
    ticket_medio: float
