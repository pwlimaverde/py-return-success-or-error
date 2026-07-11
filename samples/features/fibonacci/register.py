"""Registro de DI da feature.

Feature sem I/O: não há datasource nem repository — só UseCase → Service.
"""

from composition.container import Container
from features.fibonacci.domain.services import FibonacciService
from features.fibonacci.domain.usecases import FibonacciUsecase
from features.fibonacci.services.fibonacci_service import (
    FibonacciServiceImpl,
)


def add_fibonacci_feature(container: Container) -> Container:
    """Registra o caso de uso (background + monitor) e o service."""
    return container.add_singleton(
        FibonacciUsecase,
        lambda _: FibonacciUsecase(
            run_in_background=True, monitor_execution_time=True
        ),
    ).add_singleton(
        FibonacciService,
        lambda c: FibonacciServiceImpl(c.resolve(FibonacciUsecase)),
    )
