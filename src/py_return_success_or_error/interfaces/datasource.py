from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class Datasource(ABC, Generic[TypeDatasource, TypeParameters]):

    @abstractmethod
    def __call__(self, parameters: TypeParameters) -> TypeDatasource:
        pass  # pragma: no cover
