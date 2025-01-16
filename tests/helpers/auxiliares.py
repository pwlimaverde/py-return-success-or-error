from dataclasses import dataclass, field

from py_return_success_or_error import AppError, Datasource, ParametersReturnResult


@dataclass(kw_only=True)
class ErrorTestData(AppError):
    status_code: int

    def __str__(self) -> str:
        return f'ErrorTestData - {self.message}'


@dataclass(kw_only=True)
class PessoaParametros(ParametersReturnResult):
    nome: str
    idade: int
    error: AppError = field(default_factory=lambda: ErrorTestData(
        message='teste erro ErrorTest', status_code=400))

    def __post_init__(self):
        super().__init__(error=self.error)

    def __str__(self) -> str:
        return f'TestesParametros(nome={self.nome}, idade={self.idade}, error={self.error})'


@dataclass(kw_only=True)
class InfoParametros(ParametersReturnResult):
    informacoes: dict

    def __str__(self) -> str:
        return f'TestesParametrosGerais(informaçõess={self.informacoes}, error={self.error})'


class ExternalMock():

    def getData(self, teste_call: bool) -> bool:
        if teste_call:
            return True
        else:
            raise ValueError('Simulação de erro')


class DataSourceTest(Datasource[bool, PessoaParametros]):
    def __init__(self, external_mock: ExternalMock):
        self.__external_mock = external_mock

    def __call__(self, parameters: PessoaParametros) -> bool:
        return self.__external_mock.getData(parameters.idade > 18)
