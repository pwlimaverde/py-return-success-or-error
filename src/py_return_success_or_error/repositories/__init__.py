"""Camada anticorrupção: traduz exceções técnicas em erros de domínio."""

from py_return_success_or_error.repositories.repository import Repository
from py_return_success_or_error.repositories.repository_base import (
    RepositoryBase,
)

__all__ = [
    "Repository",
    "RepositoryBase",
]
