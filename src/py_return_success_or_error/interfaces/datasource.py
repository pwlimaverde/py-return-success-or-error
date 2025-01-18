from py_return_success_or_error.imports import (
    ABC,
    Generic,
    ParametersReturnResult,
    TypeVar,
    abstractmethod,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class Datasource(ABC, Generic[TypeDatasource, TypeParameters]):

    @abstractmethod
    def __call__(self, parameters: TypeParameters) -> TypeDatasource:
        pass  # pragma: no cover
