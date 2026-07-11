"""Camada anticorrupção da feature."""

from py_return_success_or_error import ErrorGeneric, NoParams, RepositoryBase

from features.check_connection.domain.errors import (
    CheckConnectionError,
    ConnectionTimeout,
)


class CheckConnectionRepository(
    RepositoryBase[bool, NoParams, CheckConnectionError]
):
    """Traduz falhas técnicas da checagem em erros da feature."""

    def map_error(
        self, exception: Exception, parameters: NoParams
    ) -> CheckConnectionError:
        match exception:
            case TimeoutError():
                return ConnectionTimeout(message=str(exception))
            case _:
                return ErrorGeneric(message=str(exception))
