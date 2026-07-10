"""Testes do singleton Unit."""

import pickle

from py_return_success_or_error.core.unit import UNIT, Unit


def test_unit_e_singleton() -> None:
    assert Unit() is UNIT
    assert Unit() is Unit()


def test_unit_str_e_repr() -> None:
    assert str(UNIT) == 'Unit - void'
    assert repr(UNIT) == 'UNIT'


def test_unit_sobrevive_ao_pickle() -> None:
    assert pickle.loads(pickle.dumps(UNIT)) is UNIT
