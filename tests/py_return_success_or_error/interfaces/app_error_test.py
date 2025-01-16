from dataclasses import dataclass

from py_return_success_or_error import AppError, ErrorGeneric


class ErrorTest(AppError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code

    def __str__(self) -> str:
        return f'ErrorTest - {self.message}'


@dataclass(kw_only=True)
class ErrorTest2(AppError):
    status_code: int

    def __str__(self) -> str:
        return f'ErrorTest - {self.message}'


def testInstanciaAppError():
    erro_generic = ErrorGeneric('teste erro ErrorGeneric')
    erro_test = ErrorTest('teste erro ErrorTest', 400)
    erro_test2 = ErrorTest2('teste erro ErrorTest', status_code=400)
    erro_test2_copy = ErrorTest2('teste erro ErrorTest', status_code=400)

    assert isinstance(erro_generic, AppError)
    assert erro_generic.message == 'teste erro ErrorGeneric'
    assert isinstance(erro_test, ErrorTest)
    assert erro_test.message == 'teste erro ErrorTest'
    assert erro_test.status_code == 400
    assert erro_test2_copy == erro_test2
    assert str(erro_generic) == "ErrorGeneric - teste erro ErrorGeneric"
