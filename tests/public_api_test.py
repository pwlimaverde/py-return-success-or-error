"""Smoke test da superfície pública: tudo importável a partir da raiz."""

import py_return_success_or_error as lib


def test_todos_os_simbolos_publicos_importaveis() -> None:
    for nome in lib.__all__:
        assert hasattr(lib, nome), f'símbolo ausente na raiz: {nome}'


def test_api_antiga_removida() -> None:
    for antigo in (
        'SuccessReturn',
        'ErrorReturn',
        'ParametersReturnResult',
        'Datasource',
        'EMPTY',
        'Empty',
    ):
        assert not hasattr(lib, antigo), f'API 0.x ainda exposta: {antigo}'
