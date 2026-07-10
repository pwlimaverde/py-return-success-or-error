# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versionamento [SemVer](https://semver.org/lang/pt-BR/).

## 1.0.0rc1 — 2026-07-08

Reescrita completa da biblioteca. **Todos os itens abaixo são breaking changes** — a API 0.x foi removida.

### Adicionado
- `ReturnSuccessOrError[TValue, TError]`: união fechada `Success | Failure` com **erro parametrizado por feature** (PEP 695 `type` alias). Consumo exaustivo via `match/case` + `assert_never`, provado pelo mypy/pyright.
- `Success[TValue]` / `Failure[TError]`: dataclasses congeladas com igualdade por valor; função `match()` para consumo funcional.
- `Unit`/`UNIT` (operação sem retorno) e `Nil`/`NIL` (nulo como resultado válido) — singletons selados e pickle-safe.
- `AppError` como **valor imutável** (não herda mais de `Exception`), com `with_message()` preservando o tipo concreto; `ErrorGeneric` para o caso inesperado.
- Arquitetura em camadas: `DataSource` (porta burra async que lança), `Repository`/`RepositoryBase` (anticorrupção com `map_error` abstrato), `UsecaseBase` e `UsecaseBaseCallData` (FETCH → CURTO-CIRCUITO → PROCESS).
- `UsecaseExecutorBase` com `run_in_background` (despacho do `process` CPU-bound via `asyncio.to_thread`), `monitor_execution_time` + `on_execution_time_measured`, `on_unexpected` abstrato e fábricas `ok`/`fail`.
- `_dispatch_to_background` **sobrescrevível**: o despacho de background é um ponto de extensão — plugue `InterpreterPoolExecutor` (Python 3.14+, PEP 734) ou `ProcessPoolExecutor` para paralelismo real de CPU; no CPython free-threaded (3.14+, PEP 779) o padrão em thread já dá paralelismo real. Suporte declarado a Python 3.13 e 3.14.
- Semântica de cancelamento asyncio: `CancelledError` **sempre propaga** (nunca vira `Failure`); cancelamento pendente é entregue antes do `process` nos dois modos de execução.
- `samples/` com três features completas (check_connection, fibonacci, sales_report) organizadas em camadas (`domain/{errors,models,parameters,services,usecases}` + `datasources/`, `repositories/`, `services/`): contrato do service como ABC no domínio, implementação `XxxServiceImpl` na camada externa, `add_xxx_feature(container)` registrando contrato → implementação e agregador `add_features` — **DI mora inteiramente fora do core**. Padrão documentado em `samples/README.md`.
- Tipagem estrita como feature: `mypy --strict` em src, tests e samples; pacote continua PEP 561 (`py.typed`).

### Alterado
- Execução **async-first**: usecases, repositories e datasources são invocados com `await objeto(parameters)`.
- Versão mínima do Python continua **3.13**, agora usando generics PEP 695 e `type` statements.

### Removido (mapa de migração)

| 0.x | 1.0 |
|---|---|
| `SuccessReturn(valor)` | `Success(valor)` / `self.ok(valor)` |
| `ErrorReturn(erro)` | `Failure(erro)` / `self.fail(erro)` |
| `ReturnSuccessOrError[T]` (erro fixo) | `ReturnSuccessOrError[TValue, TError]` |
| `AppError(Exception)` | `AppError` (valor, sem `Exception`) |
| `ParametersReturnResult.error` | `Parameters` — só dados; erro por camada |
| `Datasource.__call__` síncrono | `DataSource.__call__` async |
| `RepositoryMixin._resultDatasource` | `RepositoryBase.map_error(exception, params)` |
| `ThreadMixin.runNewThread` | `run_in_background=True` |
| `EMPTY` / `Empty` | `UNIT` ou `NIL` |
| `imports.py` (hub interno) | removido — importe da raiz do pacote |

### Notas de design
- Composição/DI **não mora no core**: nenhum tipo de container, marker interface ou registro na biblioteca — a convenção é documentada no README §Composição e demonstrada nos samples com um container de ~30 linhas feito à mão.
- Não há erro universal: `map_error` e `on_unexpected` são abstratos porque cada feature decide para qual caso do seu conjunto fechado cada falha converge.
- `process` é **síncrono** (CPU-bound) por design — é o que dá sentido ao `run_in_background`. I/O pertence ao `DataSource`.

## 0.6.1
- Correção da documentação.

## 0.6.0
- Correção do `TypeError` em `testUsecaseBaseCallDataSucesso` e `testUsecaseBaseCallDataErro` no arquivo `usecase_base_test.py` ao instanciar `PessoaParametros` e `InfoParametros` sem o argumento `error`.
- Adição de `field(default_factory=lambda: ErrorTestData(message='teste erro ErrorTest', status_code=400))` ao atributo `error` nas classes `PessoaParametros` e `InfoParametros` em `tests/helpers/auxiliares_mock.py`, tornando o argumento opcional e fornecendo um valor padrão.

## 0.5.3
1 - Correção de bug. Adicionada lista `__all__` no `__init__.py` para resolver erro do MyPy "Module does not explicitly export attribute"
