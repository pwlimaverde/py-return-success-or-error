from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union

from py_return_success_or_error.interfaces.app_error import AppError

R = TypeVar('R')


class ReturnSuccessOrError(ABC, Generic[R]):
    def __init__(self, success: Optional[R] = None, error: Optional[AppError] = None) -> None:
        """Inicializa a classe com um valor ou um erro."""
        if success is not None and error is not None:
            raise ValueError(
                "Não pode definir 'success' e 'error' ao mesmo tempo.")  # pragma: no cover
        self.__success = success
        self.__error = error

    @property
    def result(self) -> Union[R, AppError]:
        """Retorna o success ou o erro."""
        if isinstance(self, SuccessReturn):
            if self.__success is None:
                raise ValueError("Não pode retornar um valor nulo.")
            return self.__success
        elif isinstance(self, ErrorReturn):
            if self.__error is None:
                raise ValueError("Não pode retornar um valor nulo.")
            return self.__error
        else:
            raise ValueError("SubClass Invalida.")

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação do success ou erro."""


class SuccessReturn(ReturnSuccessOrError[R]):
    def __init__(self, success: R) -> None:
        """Inicializa a classe com um valor."""
        super().__init__(success=success)

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'Success: {self.result}'


class ErrorReturn(ReturnSuccessOrError[R]):
    def __init__(self, error: AppError) -> None:
        """Inicializa a classe com um valor."""
        super().__init__(error=error)

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'Error: {self.result}'
