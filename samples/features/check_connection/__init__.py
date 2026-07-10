"""API pública da feature CheckConnection.

O consumidor importa daqui — contrato do service, erros e a função de
registro — sem conhecer a estrutura interna de camadas.
"""

from features.check_connection.domain.errors import (
    CheckConnectionError,
    ConnectionTimeout,
    Offline,
)
from features.check_connection.domain.services import CheckConnectionService
from features.check_connection.register import add_check_connection_feature

__all__ = [
    'CheckConnectionError',
    'CheckConnectionService',
    'ConnectionTimeout',
    'Offline',
    'add_check_connection_feature',
]
