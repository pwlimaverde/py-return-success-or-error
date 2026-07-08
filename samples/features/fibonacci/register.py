"""Registro da feature Fibonacci (≙ AddFibonacciFeature)."""

from composition.container import Container
from features.fibonacci.services import FibonacciService
from features.fibonacci.usecases import FibonacciUsecase


def add_fibonacci_feature(container: Container) -> Container:
    """Registra o caso de uso (background + monitor) e o service."""
    return container.add_singleton(
        FibonacciUsecase,
        lambda _: FibonacciUsecase(
            run_in_background=True, monitor_execution_time=True
        ),
    ).add_singleton(
        FibonacciService,
        lambda c: FibonacciService(c.resolve(FibonacciUsecase)),
    )
