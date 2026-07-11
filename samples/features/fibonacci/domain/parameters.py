"""Parâmetros da feature — só dados."""

from dataclasses import dataclass

from py_return_success_or_error import Parameters


@dataclass(frozen=True)
class FibonacciParameters(Parameters):
    posicao: int
