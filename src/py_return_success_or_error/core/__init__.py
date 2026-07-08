"""Núcleo da biblioteca: o tipo de resultado e os singletons de valor."""

from py_return_success_or_error.core.nil import NIL, Nil
from py_return_success_or_error.core.return_success_or_error import (
    Failure,
    ReturnSuccessOrError,
    Success,
    match,
)
from py_return_success_or_error.core.unit import UNIT, Unit

__all__ = [
    "NIL",
    "UNIT",
    "Failure",
    "Nil",
    "ReturnSuccessOrError",
    "Success",
    "Unit",
    "match",
]
