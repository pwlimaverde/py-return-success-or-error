from py_return_success_or_error import ErrorReturn, ReturnSuccessOrError, SuccessReturn
from tests.helpers import (
    DataSourceTest,
    ErrorTestData,
    ExternalMock,
    InfoParametros,
    PessoaParametros,
    UsecaseBaseCallDataTest,
    UsecaseBaseTest,
)


def testUsecaseBaseCallDataSucesso():
    external_mock = ExternalMock()
    datasource_mock = DataSourceTest(external_mock)
    parametros_mock = PessoaParametros(nome='teste', idade=18)
    usecase = UsecaseBaseCallDataTest(datasource_mock)
    result = usecase(parametros_mock)

    assert isinstance(result, ReturnSuccessOrError)

    if isinstance(result, SuccessReturn):
        assert result.result == 'Maior de idade'
    else:
        assert False, "Resultado inesperado"


def testUsecaseBaseCallDataErro():
    external_mock = ExternalMock()
    datasource_mock = DataSourceTest(external_mock)
    parametros_mock = PessoaParametros(nome='teste', idade=16)
    usecase = UsecaseBaseCallDataTest(datasource_mock)
    result = usecase(parametros_mock)

    assert isinstance(result, ReturnSuccessOrError)

    if isinstance(result, ErrorReturn):
        assert isinstance(result.result, ErrorTestData)
        assert result.result.message == 'teste erro ErrorTest'
    else:
        assert False, "Resultado inesperado"


def testUsecaseBaseSucesso():
    parametros_mock = InfoParametros(informacoes={'teste': 'teste usecase'}, error=ErrorTestData(
        message='teste erro ErrorTest', status_code=400))
    usecase = UsecaseBaseTest()
    result = usecase(parametros_mock)

    assert isinstance(result, ReturnSuccessOrError)

    if isinstance(result, SuccessReturn):
        assert result.result
    else:
        assert False, "Resultado inesperado"


def testUsecaseBaseErrro():
    parametros_mock = InfoParametros(informacoes={'teste': 'teste usecase erro'}, error=ErrorTestData(
        message='teste erro ErrorTest', status_code=400))
    usecase = UsecaseBaseTest()
    result = usecase(parametros_mock)

    assert isinstance(result, ReturnSuccessOrError)

    if isinstance(result, ErrorReturn):
        assert isinstance(result.result, ErrorTestData)
        assert result.result.message == 'teste erro ErrorTest'
    else:
        assert False, "Resultado inesperado"
