"""Modelo de erro: erros são valores imutáveis, não exceções."""

from py_return_success_or_error.errors.app_error import AppError
from py_return_success_or_error.errors.error_generic import ErrorGeneric

__all__ = [
    "AppError",
    "ErrorGeneric",
]
