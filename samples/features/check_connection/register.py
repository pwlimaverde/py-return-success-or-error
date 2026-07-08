"""Registro da feature CheckConnection (≙ AddCheckConnectionFeature)."""

from composition.container import Container
from features.check_connection.datasources import FakeConnectivityDataSource
from features.check_connection.repositories import CheckConnectionRepository
from features.check_connection.services import CheckConnectionService
from features.check_connection.usecases import CheckConnectionUsecase


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
            lambda c: CheckConnectionService(
                c.resolve(CheckConnectionUsecase)
            ),
        )
    )
