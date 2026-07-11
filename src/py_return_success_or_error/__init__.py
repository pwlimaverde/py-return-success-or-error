"""py-return-success-or-error — Result/Either com erro fechado por feature.

Superfície pública da biblioteca: importe tudo a partir da raiz do pacote::

    from py_return_success_or_error import (
        Success, Failure, ReturnSuccessOrError, UsecaseBase, ...
    )
"""

from py_return_success_or_error.core.nil import NIL, Nil
from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
    match,
)
from py_return_success_or_error.core.unit import UNIT, Unit
from py_return_success_or_error.datasources.datasource import DataSource
from py_return_success_or_error.errors.app_error import AppError
from py_return_success_or_error.errors.error_generic import ErrorGeneric
from py_return_success_or_error.parameters.no_params import NO_PARAMS, NoParams
from py_return_success_or_error.parameters.parameters import Parameters
from py_return_success_or_error.repositories.repository import Repository
from py_return_success_or_error.repositories.repository_base import (
    RepositoryBase,
)
from py_return_success_or_error.usecases.usecase_base import UsecaseBase
from py_return_success_or_error.usecases.usecase_base_call_data import (
    UsecaseBaseCallData,
)
from py_return_success_or_error.usecases.usecase_executor_base import (
    UsecaseExecutorBase,
)

__all__ = [
    "NIL",
    "NO_PARAMS",
    "UNIT",
    "AppError",
    "DataSource",
    "ErrorGeneric",
    "Failure",
    "Nil",
    "NoParams",
    "Parameters",
    "Repository",
    "RepositoryBase",
    "ReturnSuccessOrError",
    "Success",
    "Unit",
    "UsecaseBase",
    "UsecaseBaseCallData",
    "UsecaseExecutorBase",
    "match",
]
