"""Parâmetros da feature — só dados."""

from dataclasses import dataclass

from py_return_success_or_error import Parameters


@dataclass(frozen=True)
class SalesReportParameters(Parameters):
    valor_minimo: float
