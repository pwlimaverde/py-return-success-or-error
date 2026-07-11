"""Registro de DI da feature.

Encadeia as camadas — DataSource → Repository → UseCase → Service — e
expõe o CONTRATO (``CheckConnectionService``), nunca a implementação.
"""

from composition.container import Container
from features.check_connection.datasources.fake_connectivity_datasource import (  # noqa: E501
    FakeConnectivityDataSource,
)
from features.check_connection.domain.services import CheckConnectionService
from features.check_connection.domain.usecases import CheckConnectionUsecase
from features.check_connection.repositories.check_connection_repository import (  # noqa: E501
    CheckConnectionRepository,
)
from features.check_connection.services.check_connection_service import (
    CheckConnectionServiceImpl,
)


def add_check_connection_feature(container: Container) -> Container:
    """Registra todas as camadas da feature no container."""
    return (
        container.add_singleton(
            FakeConnectivityDataSource,
            lambda _: FakeConnectivityDataSource(online=True),
        )
        .add_singleton(
            CheckConnectionRepository,
            lambda c: CheckConnectionRepository(
                c.resolve(FakeConnectivityDataSource)
            ),
        )
        .add_singleton(
            CheckConnectionUsecase,
            lambda c: CheckConnectionUsecase(
                c.resolve(CheckConnectionRepository)
            ),
        )
        .add_singleton(
            CheckConnectionService,
            lambda c: CheckConnectionServiceImpl(
                c.resolve(CheckConnectionUsecase)
            ),
        )
    )
