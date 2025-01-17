from tests.helpers import (
    DataSourceTest,
    ExternalMock,
    PessoaParametros,
    UsecaseBaseCallDataTest,
)


def testUsecaseBaseCallData():
    external_mock = ExternalMock()
    datasource_mock = DataSourceTest(external_mock)
    parametros_mock = PessoaParametros(nome='teste', idade=18)
    usecase = UsecaseBaseCallDataTest(datasource_mock)
    print()
    print('******')
    print(usecase(parametros_mock))
    print('******')
