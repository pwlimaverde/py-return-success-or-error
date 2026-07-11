"""Testes dos parâmetros."""

import pickle
from dataclasses import dataclass

import pytest

from py_return_success_or_error.parameters.no_params import NO_PARAMS, NoParams
from py_return_success_or_error.parameters.parameters import Parameters


@dataclass(frozen=True)
class BuscaClienteParameters(Parameters):
    cliente_id: int


def test_parameters_nao_e_instanciavel() -> None:
    with pytest.raises(TypeError):
        Parameters()


def test_no_params_e_parameters() -> None:
    assert isinstance(NO_PARAMS, Parameters)


def test_no_params_e_singleton() -> None:
    assert NoParams() is NO_PARAMS


def test_no_params_sobrevive_ao_pickle() -> None:
    assert pickle.loads(pickle.dumps(NO_PARAMS)) is NO_PARAMS


def test_parametros_customizados_sao_so_dados() -> None:
    params = BuscaClienteParameters(cliente_id=7)
    assert params.cliente_id == 7
    assert not hasattr(params, 'error')  # breaking vs 0.x


def test_parametros_igualdade_por_valor() -> None:
    assert BuscaClienteParameters(cliente_id=1) == BuscaClienteParameters(
        cliente_id=1
    )


def test_parametros_sao_imutaveis() -> None:
    params = BuscaClienteParameters(cliente_id=1)
    with pytest.raises(AttributeError):
        params.cliente_id = 2  # type: ignore[misc]
