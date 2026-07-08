"""Casos de uso: orquestração, regra de negócio e fronteira do inesperado."""

from py_return_success_or_error.usecases.usecase_base import UsecaseBase
from py_return_success_or_error.usecases.usecase_base_call_data import (
    UsecaseBaseCallData,
)
from py_return_success_or_error.usecases.usecase_executor_base import (
    UsecaseExecutorBase,
)

__all__ = [
    "UsecaseBase",
    "UsecaseBaseCallData",
    "UsecaseExecutorBase",
]
