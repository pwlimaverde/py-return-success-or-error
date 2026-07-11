"""Testes do singleton Nil."""

import pickle

from py_return_success_or_error.core.nil import NIL, Nil


def test_nil_e_singleton() -> None:
    assert Nil() is NIL
    assert Nil() is Nil()


def test_nil_str_e_repr() -> None:
    assert str(NIL) == 'Nil - null'
    assert repr(NIL) == 'NIL'


def test_nil_sobrevive_ao_pickle() -> None:
    assert pickle.loads(pickle.dumps(NIL)) is NIL
