from tests.helpers import DataSourceTest, ExternalMock, PessoaParametros


def testeDataSourceSucesso():
    external_mock = ExternalMock()
    datasource_test = DataSourceTest(external_mock)
    parameters = PessoaParametros(nome='teste', idade=20)
    result = datasource_test(parameters)
    assert result


def testeDataSourceErro():
    external_mock = ExternalMock()
    datasource_test = DataSourceTest(external_mock)
    parameters = PessoaParametros(nome='teste', idade=17)
    try:
        result = datasource_test(parameters)
        assert False
    except ValueError as e:
        assert e.args[0] == 'Simulação de erro'
