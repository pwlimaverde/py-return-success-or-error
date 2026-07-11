"""Container de DI mínimo, feito à mão — a lib NÃO exige container algum.

Este container existe só para demonstrar a convenção de composição.
Em projetos reais, use o que preferir: ``dependency-injector``, ``punq``,
wiring manual por construtores... A biblioteca não conhece nada disso.
"""

from collections.abc import Callable
from typing import cast


class Container:
    """Registro de fábricas com resolução singleton por tipo."""

    def __init__(self) -> None:
        self._factories: dict[type, Callable[['Container'], object]] = {}
        self._singletons: dict[type, object] = {}

    def add_singleton[T](
        self,
        registration: type[T],
        factory: Callable[['Container'], T],
    ) -> 'Container':
        """Registra a fábrica de ``registration`` (resolvida uma única vez)."""
        self._factories[registration] = factory
        return self

    def resolve[T](self, registration: type[T]) -> T:
        """Resolve (e memoriza) a instância registrada para o tipo."""
        if registration not in self._singletons:
            self._singletons[registration] = self._factories[registration](
                self
            )
        return cast(T, self._singletons[registration])
