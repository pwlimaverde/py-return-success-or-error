from py_return_success_or_error.imports import (
    ABC,
    abstractmethod,
    dataclass,
    field,
)
from py_return_success_or_error.interfaces.app_error import AppError, ErrorGeneric


@dataclass
class ParametersReturnResult(ABC, Exception):
    error: AppError

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação do success ou erro."""


@dataclass
class NoParams(ParametersReturnResult):
    error: AppError = field(
        default_factory=lambda: ErrorGeneric(message='General Error'))

    def __str__(self):
        return self.__repr__()
