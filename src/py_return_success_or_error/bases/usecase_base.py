from py_return_success_or_error.imports import (
    ABC,
    Datasource,
    Generic,
    ParametersReturnResult,
    RepositoryMixin,
    ReturnSuccessOrError,
    ThreadMixin,
    TypeVar,
    abstractmethod,
)

TypeUsecase = TypeVar('TypeUsecase')
TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class UsecaseBase(
        ABC, Generic[TypeUsecase, TypeParameters], ThreadMixin):

    @abstractmethod
    def __call__(
            self, parameters: TypeParameters) -> ReturnSuccessOrError[TypeUsecase]:
        pass   # pragma: no cover


class UsecaseBaseCallData(
        ABC, Generic[TypeUsecase, TypeDatasource, TypeParameters], RepositoryMixin, ThreadMixin):

    def __init__(
            self, datasource: Datasource[TypeDatasource, TypeParameters]) -> None:
        self._datasource = datasource

    @abstractmethod
    def __call__(
            self, parameters: TypeParameters) -> ReturnSuccessOrError[TypeUsecase]:
        pass   # pragma: no cover
