"""Testes do modelo de erro (≙ AppErrorTests.cs)."""

import pytest

from py_return_success_or_error.errors.app_error import AppError
from py_return_success_or_error.errors.error_generic import ErrorGeneric
from tests.helpers.test_errors import ValidationError


def test_app_error_nao_e_instanciavel() -> None:
    with pytest.raises(TypeError):
        AppError(message='x')


def test_igualdade_por_valor() -> None:
    assert ErrorGeneric(message='a') == ErrorGeneric(message='a')
    assert ErrorGeneric(message='a') != ErrorGeneric(message='b')


def test_error_generic_str() -> None:
    assert str(ErrorGeneric(message='boom')) == 'ErrorGeneric - boom'


def test_erro_e_imutavel() -> None:
    with pytest.raises(AttributeError):
        ErrorGeneric(message='a').message = 'b'  # type: ignore[misc]


def test_with_message_em_error_generic() -> None:
    original = ErrorGeneric(message='antes')
    novo = original.with_message('depois')
    assert novo == ErrorGeneric(message='depois')
    assert original.message == 'antes'


def test_with_message_preserva_tipo_concreto_e_campos() -> None:
    original = ValidationError(message='antes', field='email')
    novo = original.with_message('depois')
    assert type(novo) is ValidationError
    assert novo.field == 'email'
    assert novo.message == 'depois'


def test_erro_nao_e_excecao() -> None:
    assert not isinstance(ErrorGeneric(message='x'), BaseException)
