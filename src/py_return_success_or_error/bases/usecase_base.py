from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py_return_success_or_error.core.return_success_or_error import ReturnSuccessOrError
from py_return_success_or_error.interfaces.datasource import Datasource
from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)
from py_return_success_or_error.mixins.repository_mixin import RepositoryMixin
from py_return_success_or_error.mixins.thread_mixin import ThreadMixin

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
