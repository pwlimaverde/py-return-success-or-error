from typing import TypeVar

from py_return_success_or_error.core.return_success_or_error import (
    ErrorReturn,
    ReturnSuccessOrError,
    SuccessReturn,
)
from py_return_success_or_error.interfaces.datasource import Datasource
from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class RepositoryMixin():

    def resultDatasource(
        self,
        parameters: TypeParameters,
        datasource: Datasource[TypeDatasource, TypeParameters]
    ) -> ReturnSuccessOrError[TypeDatasource]:
        try:
            result = datasource(parameters)
            return SuccessReturn(result)
        except Exception:
            return ErrorReturn(parameters.error)
