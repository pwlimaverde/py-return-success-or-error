from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)

R = TypeVar('R')
P = TypeVar('P', bound=ParametersReturnResult)


class Datasource(ABC, Generic[R, P]):

    @abstractmethod
    def __call__(self, parameters: P) -> R:
        pass  # pragma: no cover
