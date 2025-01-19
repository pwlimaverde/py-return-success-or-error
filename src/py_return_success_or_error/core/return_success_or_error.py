from py_return_success_or_error.imports import (
    ABC,
    Generic,
    Optional,
    TypeVar,
    Union,
    abstractmethod,
)
from py_return_success_or_error.interfaces.app_error import AppError

TypeData = TypeVar('TypeData')


class ReturnSuccessOrError(ABC, Generic[TypeData]):
    """Classe base abstrata para representar o retorno de uma operação com sucesso ou erro.

    Attributes:
        __success (Optional[TypeData]): Valor de sucesso da operação.
        __error (Optional[AppError]): Instância de AppError que descreve o erro ocorrido.
    """
    def __init__(self, success: Optional[TypeData] = None,
                error: Optional[AppError] = None) -> None:
        """Inicializa a classe com um valor de sucesso ou um erro.

        Args:
            success (Optional[TypeData]): Valor de sucesso da operação.
            error (Optional[AppError]): Instância de AppError que descreve o erro ocorrido.

        Raises:
            ValueError: Se ambos 'success' e 'error' forem definidos ao mesmo tempo.
        """
        if success is not None and error is not None:
            raise ValueError(
                "Não pode definir 'success' e 'error' ao mesmo tempo.")  # pragma: no cover
        self.__success = success
        self.__error = error

    @property
    def result(self) -> Union[TypeData, AppError]:
        """Retorna o valor de sucesso ou o erro.

        Returns:
            Union[TypeData, AppError]: Valor de sucesso ou instância de AppError.

        Raises:
            ValueError: Se o valor de sucesso for nulo.
        """
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


class SuccessReturn(ReturnSuccessOrError[TypeData]):
    """Classe que representa o retorno de uma operação bem-sucedida.

    Attributes:
        __success (TypeData): Valor de sucesso da operação.
    """
    def __init__(self, success: TypeData) -> None:
        """Inicializa a classe com um valor de sucesso.

        Args:
            success (TypeData): Valor de sucesso da operação.
        """
        super().__init__(success=success)

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'Success: {self.result}'


class ErrorReturn(ReturnSuccessOrError[TypeData]):
    """Classe que representa o retorno de uma operação com erro.

    Attributes:
        __error (AppError): Instância de AppError que descreve o erro ocorrido.
    """
    def __init__(self, error: AppError) -> None:
        """Inicializa a classe com um valor."""
        super().__init__(error=error)

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'Error: {self.result}'
