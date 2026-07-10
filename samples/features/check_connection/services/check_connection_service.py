"""Implementação do contrato do service."""

from py_return_success_or_error import NO_PARAMS, ReturnSuccessOrError

from features.check_connection.domain.errors import CheckConnectionError
from features.check_connection.domain.services import CheckConnectionService
from features.check_connection.domain.usecases import CheckConnectionUsecase


class CheckConnectionServiceImpl(CheckConnectionService):
    """Fachada fina sobre o caso de uso."""

    def __init__(self, usecase: CheckConnectionUsecase) -> None:
        self._usecase = usecase

    async def check(
        self,
    ) -> ReturnSuccessOrError[str, CheckConnectionError]:
        return await self._usecase(NO_PARAMS)
