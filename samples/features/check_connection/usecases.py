"""Caso de uso da feature CheckConnection."""

from py_return_success_or_error import (
    ErrorGeneric,
    NoParams,
    ReturnSuccessOrError,
    UsecaseBaseCallData,
)

from features.check_connection.errors import CheckConnectionError, Offline


class CheckConnectionUsecase(
    UsecaseBaseCallData[str, bool, NoParams, CheckConnectionError]
):
    """Converte o estado bruto de conectividade na mensagem do domínio."""

    def process(
        self, data: bool, parameters: NoParams
    ) -> ReturnSuccessOrError[str, CheckConnectionError]:
        if not data:
            return self.fail(Offline(message='sem acesso à rede'))
        return self.ok('Conectado')

    def on_unexpected(self, exception: Exception) -> CheckConnectionError:
        return ErrorGeneric(message=str(exception))
