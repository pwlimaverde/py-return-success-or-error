"""Asserções que estreitam o resultado (≙ ResultAssertions.cs)."""

from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
)


def assert_success[TValue, TError](
    result: ReturnSuccessOrError[TValue, TError],
) -> TValue:
    """Afirma que o resultado é ``Success`` e devolve o valor."""
    assert isinstance(result, Success), f'esperava Success, veio {result}'
    return result.value


def assert_failure[TValue, TError](
    result: ReturnSuccessOrError[TValue, TError],
) -> TError:
    """Afirma que o resultado é ``Failure`` e devolve o erro."""
    assert isinstance(result, Failure), f'esperava Failure, veio {result}'
    return result.error
