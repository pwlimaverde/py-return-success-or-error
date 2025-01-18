from py_return_success_or_error.imports import (
    Datasource,
    ErrorReturn,
    ParametersReturnResult,
    ReturnSuccessOrError,
    SuccessReturn,
    TypeVar,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class RepositoryMixin():

    def _resultDatasource(
        self,
        parameters: TypeParameters,
        datasource: Datasource[TypeDatasource, TypeParameters]
    ) -> ReturnSuccessOrError[TypeDatasource]:
        try:
            result = datasource(parameters)
            return SuccessReturn(result)
        except Exception:
            return ErrorReturn(parameters.error)
