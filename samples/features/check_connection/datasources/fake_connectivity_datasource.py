"""Porta de dados da feature — fake para o sample."""

import asyncio

from py_return_success_or_error import DataSource, NoParams


class FakeConnectivityDataSource(DataSource[bool, NoParams]):
    """Simula a checagem de conectividade: devolve o estado ou estoura."""

    def __init__(
        self, *, online: bool = True, simular_timeout: bool = False
    ) -> None:
        self._online = online
        self._simular_timeout = simular_timeout

    async def __call__(self, parameters: NoParams) -> bool:
        await asyncio.sleep(0)  # simula I/O
        if self._simular_timeout:
            raise TimeoutError('ping excedeu 3s')
        return self._online
