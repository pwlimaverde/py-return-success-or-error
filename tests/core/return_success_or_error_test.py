"""Testes do tipo de resultado (≙ ReturnSuccessOrErrorTests.cs)."""

from typing import assert_never

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
    match,
)
from tests.helpers.assertions import assert_failure, assert_success
from tests.helpers.test_errors import (
    NotFoundError,
    TestError,
    ValidationError,
    text,
)


def test_success_igualdade_por_valor() -> None:
    assert Success(42) == Success(42)
    assert Success(42) != Success(43)


def test_failure_igualdade_por_valor() -> None:
    erro = NotFoundError(message='sumiu')
    assert Failure(erro) == Failure(NotFoundError(message='sumiu'))
    assert Failure(erro) != Failure(NotFoundError(message='outro'))


def test_success_diferente_de_failure() -> None:
    assert Success(1) != Failure(1)  # type: ignore[comparison-overlap]


def test_success_e_imutavel() -> None:
    import pytest

    with pytest.raises(AttributeError):
        Success(1).value = 2  # type: ignore[misc]


def test_str_de_success_e_failure() -> None:
    assert str(Success(7)) == 'Success: 7'
    erro = NotFoundError(message='x')
    assert str(Failure(erro)) == f'Failure: {erro}'


def test_match_executa_ramo_de_sucesso() -> None:
    result: ReturnSuccessOrError[int, TestError] = Success(10)
    texto = match(
        result,
        on_success=lambda value: f'valor {value}',
        on_error=text,
    )
    assert texto == 'valor 10'


def test_match_executa_ramo_de_erro() -> None:
    result: ReturnSuccessOrError[int, TestError] = Failure(
        ValidationError(message='obrigatório', field='nome')
    )
    texto = match(
        result,
        on_success=lambda value: f'valor {value}',
        on_error=text,
    )
    assert texto == 'inválido[nome]: obrigatório'


def test_match_case_exaustivo_com_assert_never() -> None:
    """O padrão canônico de consumo — o mypy prova a cobertura."""
    result: ReturnSuccessOrError[int, TestError] = Success(5)
    match result:
        case Success(value):
            assert value == 5
        case Failure(error):
            raise AssertionError(f'não deveria falhar: {error}')
        case _:
            assert_never(result)


def test_union_de_erro_da_feature_exaustivo() -> None:
    """Consumo exaustivo do union de erro, sem braço default."""
    erro: TestError = NotFoundError(message='cliente 9')
    assert text(erro) == 'não encontrado: cliente 9'


def test_assertions_estreitam_o_payload() -> None:
    ok: ReturnSuccessOrError[str, TestError] = Success('dado')
    falha: ReturnSuccessOrError[str, TestError] = Failure(
        NotFoundError(message='x')
    )
    assert assert_success(ok) == 'dado'
    assert assert_failure(falha) == NotFoundError(message='x')
