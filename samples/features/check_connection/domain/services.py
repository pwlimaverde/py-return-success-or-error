"""Contrato do service da feature.

O contrato vive no domínio; a implementação vive na camada externa
(``services/``). A UI depende só deste contrato.
"""

from abc import ABC, abstractmethod

from py_return_success_or_error import ReturnSuccessOrError

from features.check_connection.domain.errors import CheckConnectionError


class CheckConnectionService(ABC):
    """Ponto de entrada público da feature — o que a UI consome."""

    @abstractmethod
    async def check(
        self,
    ) -> ReturnSuccessOrError[str, CheckConnectionError]:
        """Verifica a conectividade e devolve a mensagem do domínio."""
