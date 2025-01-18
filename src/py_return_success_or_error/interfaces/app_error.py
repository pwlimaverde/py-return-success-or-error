from py_return_success_or_error.imports import (
    ABC,
    abstractmethod,
    dataclass,
)


@dataclass(kw_only=True)
class AppError(ABC, Exception):
    message: str

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação em string do erro."""


@dataclass
class ErrorGeneric(AppError):
    def __str__(self) -> str:
        """Retorna a representação em string do erro genérico."""
        return f'ErrorGeneric - {self.message}'
