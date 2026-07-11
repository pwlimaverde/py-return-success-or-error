# Modernização py-return-success-or-error → 1.0.0rc1 (estilo da lib C# ReturnSuccessOrError)

## Contexto

A lib Python `py-return-success-or-error` (0.6.1) implementa um Result/Either com erro fixo (`AppError` sempre), erro de fallback embutido nos parâmetros (`ParametersReturnResult.error`), `AppError` como dataclass+Exception, e execução síncrona com `ThreadMixin`. A lib irmã em C# (`C:\PROJETOS\C#\PACKAGES\return-success-or-error`, 1.0.0-preview.1) evoluiu para uma arquitetura muito superior: **erro parametrizado por feature** (`ReturnSuccessOrError<TValue, TError>` com union fechada), erros como valores imutáveis, `Parameters` só com dados, camadas `DataSource → Repository (map_error) → Usecase (process/on_unexpected)`, execução async com cancelamento, e **composição/DI totalmente fora do core** (convenção documentada de `AddXxxFeature()` + agregador).

O objetivo é reescrever a lib Python espelhando essa arquitetura em Python idiomático.

**Decisões do usuário:**
- Reescrita total com quebra (API 0.x removida), versão **1.0.0rc1**
- **Async-first** (asyncio); `process()` **síncrono** (CPU-bound, fiel ao C#)
- Invocação via **`__call__`**: `await usecase(params)`, `await datasource(params)`, `await repository(params)`
- Python **>=3.13** (generics PEP 695, `type` statements)
- Docstrings/README em pt-BR (como hoje)

## Layout final de `src/py_return_success_or_error/`

```
├── __init__.py                      # única superfície pública (__all__)
├── py.typed
├── core/
│   ├── return_success_or_error.py   # Success, Failure, type ReturnSuccessOrError, match()
│   ├── unit.py                      # Unit, UNIT
│   └── nil.py                       # Nil, NIL
├── errors/
│   ├── app_error.py                 # AppError
│   └── error_generic.py             # ErrorGeneric
├── parameters/
│   ├── parameters.py                # Parameters
│   └── no_params.py                 # NoParams, NO_PARAMS
├── datasources/datasource.py        # DataSource ABC
├── repositories/
│   ├── repository.py                # Repository ABC (interface)
│   └── repository_base.py           # RepositoryBase (camada anticorrupção)
└── usecases/
    ├── usecase_executor_base.py     # UsecaseExecutorBase
    ├── usecase_base.py              # UsecaseBase
    └── usecase_base_call_data.py    # UsecaseBaseCallData
```

**Deletar**: `bases/`, `interfaces/`, `mixins/`, `core/empty.py`, `imports.py` (anti-pattern; re-export passa a ser só via `__init__.py`), todo o conteúdo antigo de `core/return_success_or_error.py`, todos os testes antigos (`tests/py_return_success_or_error/`, `tests/helpers/auxiliares_mock.py`), `docs/api/*` antigos.

## API pública (assinaturas-chave)

### core/return_success_or_error.py
```python
@final
@dataclass(frozen=True, slots=True)
class Success[TValue]:
    value: TValue

@final
@dataclass(frozen=True, slots=True)
class Failure[TError]:
    error: TError

type ReturnSuccessOrError[TValue, TError] = Success[TValue] | Failure[TError]

def match[TValue, TError, TResult](
    result: ReturnSuccessOrError[TValue, TError], *,
    on_success: Callable[[TValue], TResult],
    on_error: Callable[[TError], TResult],
) -> TResult: ...   # match/case interno + assert_never
```
- Union type alias (não classe wrapper) = semântica do `union` C#; narrowing via `match/case` + `typing.assert_never` substitui a exaustividade do compilador.
- `match()` como função de módulo (o alias não carrega métodos) — açúcar funcional equivalente ao `Match` do C#.

### core/unit.py e core/nil.py
Singletons selados (`__new__` devolve sempre a mesma instância, `__reduce__` pickle-safe, `__slots__ = ()`): `Unit`/`UNIT` (`str` → `"Unit - void"`), `Nil`/`NIL` (`str` → `"Nil - null"`). Constantes de módulo (idioma Python, como `None`).

### errors/
```python
@dataclass(frozen=True)
class AppError(ABC):
    message: str
    def with_message(self, message: str) -> Self:      # dataclasses.replace — preserva tipo concreto
    # __post_init__ bloqueia instanciação direta de AppError

@final
@dataclass(frozen=True)
class ErrorGeneric(AppError):
    def __str__(self) -> str: return f"ErrorGeneric - {self.message}"
```
- `AppError` é **valor, não Exception** (breaking). Herdar de `AppError` é conveniência, não obrigação — `TError` pode ser qualquer tipo.
- Union fechada por feature (em samples/README, não no src): `type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric`.
- Sem `slots=True` na hierarquia `AppError` (herança dataclass+slots é frágil para subclasses do usuário).

### parameters/
```python
@dataclass(frozen=True)
class Parameters(ABC): ...       # só dados, SEM campo error (breaking)

@final
@dataclass(frozen=True)
class NoParams(Parameters): ...  # singleton
NO_PARAMS: Final[NoParams] = NoParams()
```

### datasources/ e repositories/
```python
class DataSource[TData, TParams: Parameters](ABC):
    @abstractmethod
    async def __call__(self, parameters: TParams) -> TData: ...   # porta "burra": devolve dado bruto ou LANÇA

class Repository[TData, TParams: Parameters, TError](ABC):
    @abstractmethod
    async def __call__(self, parameters: TParams) -> ReturnSuccessOrError[TData, TError]: ...

class RepositoryBase[TData, TParams: Parameters, TError](Repository[TData, TParams, TError]):
    def __init__(self, datasource: DataSource[TData, TParams]) -> None: ...
    async def __call__(self, parameters: TParams) -> ReturnSuccessOrError[TData, TError]:
        try:
            return Success(await self._datasource(parameters))
        except asyncio.CancelledError:
            raise                          # cancelamento não é falha de domínio (paridade com o catch OCE do C#)
        except Exception as exception:
            return Failure(self.map_error(exception, parameters))
    @abstractmethod
    def map_error(self, exception: Exception, parameters: TParams) -> TError: ...
```
- Sem parâmetro de cancellation token em lugar nenhum: cancelamento asyncio é ambiente (`CancelledError` nos pontos de `await`). Documentar uma vez no README ("Cancelamento").

### usecases/
```python
class UsecaseExecutorBase[TValue, TError](ABC):
    def __init__(self, *, run_in_background: bool = False, monitor_execution_time: bool = False) -> None: ...
    @abstractmethod
    def on_unexpected(self, exception: Exception) -> TError: ...      # bug → caso do union fechado
    def on_execution_time_measured(self, elapsed: timedelta) -> None: # virtual; padrão: logging DEBUG
    def ok(self, value: TValue) -> ReturnSuccessOrError[TValue, TError]:     # Success(value)
    def fail(self, error: TError) -> ReturnSuccessOrError[TValue, TError]:   # Failure(error)
    async def _measured(...)        # time.perf_counter, só quando monitor_execution_time
    async def _process_stage(...)   # ver semântica abaixo

class UsecaseBase[TValue, TParams: Parameters, TError](UsecaseExecutorBase[TValue, TError]):
    @abstractmethod
    def process(self, parameters: TParams) -> ReturnSuccessOrError[TValue, TError]: ...   # SÍNCRONO
    async def __call__(self, parameters: TParams) -> ReturnSuccessOrError[TValue, TError]: ...

class UsecaseBaseCallData[TValue, TData, TParams: Parameters, TError](UsecaseExecutorBase[TValue, TError]):
    def __init__(self, repository: Repository[TData, TParams, TError], *, run_in_background=False, monitor_execution_time=False): ...
    @abstractmethod
    def process(self, data: TData, parameters: TParams) -> ReturnSuccessOrError[TValue, TError]: ...
    async def __call__(self, parameters: TParams) -> ...:
        # FETCH (await self._repository(parameters)) → CURTO-CIRCUITO (Failure retorna direto, process NÃO roda) → PROCESS
```

**Semântica de `_process_stage`** (espelha `ProcessStageAsync` do C#, `UsecaseExecutorBase.cs:85-116`):
- Paridade direto↔background: `await asyncio.sleep(0)` antes do `process` nos dois modos (equivalente ao `ThrowIfCancellationRequested` — entrega cancelamento pendente antes da regra rodar).
- Modo direto: `process()` inline; `except Exception → Failure(self.on_unexpected(ex))`. `CancelledError` é `BaseException` no 3.13, então nunca é engolido — propaga.
- Modo background: `asyncio.to_thread(process_wrapper)` (análogo do `Task.Run`); mesma conversão de exceção dentro da thread. Documentar caveats: GIL limita paralelismo real; thread já iniciada não é interrompida pelo cancel (semântica do to_thread).
- `ok`/`fail` como métodos de instância (não static): inferem `TValue`/`TError` da subclasse — compensam a ausência de conversões implícitas do C#; forma recomendada de retornar dentro do `process`.

### `__init__.py` público
`__all__`: `Success`, `Failure`, `ReturnSuccessOrError`, `match`, `Unit`, `UNIT`, `Nil`, `NIL`, `AppError`, `ErrorGeneric`, `Parameters`, `NoParams`, `NO_PARAMS`, `DataSource`, `Repository`, `RepositoryBase`, `UsecaseExecutorBase`, `UsecaseBase`, `UsecaseBaseCallData`.

## Estratégia de exposição de features e DI (fora do core — crítico)

Igual ao C#: **zero tipos de composição/DI no src** (zero deps de runtime mantidas). A estratégia é convenção documentada + samples:

```
samples/
├── main.py                          # composition root (≙ Program.cs): roda as 3 features
├── composition/
│   ├── container.py                 # container mínimo feito à mão (~30 linhas, dict tipo→fábrica) — sem dep externa
│   └── feature_registration.py      # add_features(container) → encadeia os add_xxx_feature
└── features/
    ├── check_connection/            # errors.py (union fechada), datasources.py, repositories.py (map_error),
    │                                # usecases.py, services.py (facade), register.py (add_check_connection_feature)
    ├── fibonacci/                   # UsecaseBase pura + run_in_background=True + monitor
    └── sales_report/                # portabilidade: mesmo usecase com InMemory e Csv datasources
```

Convenção por feature (documentada no README §8 "Composição e Orquestração", espelhando o C#):
1. **Service facade** por feature (`CheckConnectionService` embrulhando o usecase)
2. **`add_xxx_feature(container)`** registrando datasource (por abstração), repository, usecase, service
3. **Agregador fino** `add_features(container)` — adicionar feature = 1 linha
4. Consumidores com `dependency-injector`/`punq`/wiring manual registram os tipos nativamente — nada da lib exige container.

Samples fora do wheel (hatchling só empacota `src/`), mas incluídos no mypy e executáveis: `uv run python samples/main.py`.

## Tipagem estrita

Tipagem é a feature estrutural (substitui a prova de exaustividade do compilador C#):
- `[tool.mypy]` no pyproject: `python_version = "3.13"`, `strict = true`, cobrindo `src`, `tests`, `samples`; `mypy` no grupo dev.
- Guia canônico de consumo: `match/case` + `case _: assert_never(error)` — mypy prova cobertura da union de erro.
- Testes de exaustividade são validados pelo mypy (não só pytest).

## Testes (pytest + pytest-asyncio, `asyncio_mode = auto`)

```
tests/
├── helpers/
│   ├── test_errors.py     # NotFoundError | ValidationError | UnexpectedError (≙ TestErrors.cs) + text() exaustivo
│   └── assertions.py      # assert_success(result) -> TValue / assert_failure(result) -> TError (≙ ResultAssertions.cs)
├── core/  return_success_or_error_test.py, unit_test.py, nil_test.py
├── errors/ app_error_test.py           # igualdade por valor, with_message preserva tipo concreto + campos
├── parameters/ parameters_test.py      # NoParams singleton, params = só dados
├── datasources/ datasource_test.py     # sucesso devolve bruto; falha lança (primeiro teste async)
├── repositories/ repository_base_test.py  # Success wrap; exceção→map_error; CancelledError propaga SEM map_error
└── usecases/
    ├── usecase_base_test.py            # ≙ 15 casos C#: resultado direto; fail(); paridade direto↔background;
    │                                   # on_unexpected nos 2 modos; cancelamento antes do process nos 2 modos;
    │                                   # CancelledError cooperativo propaga; monitor (3 casos); Unit; Nil
    └── usecase_base_call_data_test.py  # ≙ 9 casos C#: fetch→process; curto-circuito sem chamar process (spy);
                                        # caso concreto preservado; on_unexpected 2 modos; paridade; monitor; cancel
```
Padrão de teste de cancelamento: `task = asyncio.create_task(usecase(params))` → `await asyncio.sleep(0)` → `task.cancel()` → `pytest.raises(asyncio.CancelledError)`.

## Packaging / docs / CI

- **pyproject.toml**: versão `1.0.0rc1`; manter hatchling, zero deps runtime, py.typed; dev group += `pytest-asyncio`, `mypy`; adicionar `[tool.taskipy.tasks]` (test, lint, format, typecheck, docs, samples) e `[tool.mypy]`; re-lock com `uv lock`.
- **pytest.ini**: `asyncio_mode = auto`; remover `-x -s` dos addopts (hostis em CI; ficam numa task dev); **remover `--doctest-modules`** (exemplos async em docstring exigiriam wrappers `asyncio.run` — exemplos executáveis vivem nos samples/testes).
- **README.md** (pt-BR): espelhar a estrutura do README C# — Filosofia/Problema → Instalação → Início Rápido em 5 passos → Conceitos Centrais → Estrutura de Código Recomendada por feature → Fluxo de Execução (FETCH → CURTO-CIRCUITO → PROCESS) → Exemplos 1–8 culminando em "Composição e Orquestração" → Portabilidade → Modelo de Erro. Seções extras Python: "Cancelamento (asyncio)" e "Exaustividade com match/assert_never (mypy)".
- **CHANGELOG.md**: entrada 1.0.0rc1 com tabela de migração (SuccessReturn→Success, ErrorReturn→Failure, ParametersReturnResult→Parameters sem error, Datasource→DataSource async, RepositoryMixin._resultDatasource→RepositoryBase.map_error, ThreadMixin→run_in_background, EMPTY→UNIT/NIL).
- **mkdocs**: substituir `docs/api/*` por páginas dos novos módulos (mkdocstrings); atualizar nav e index.
- **CI (novo)**: `.github/workflows/ci.yml` (push/PR: uv sync → lint → mypy → pytest --cov → uv build, matrix 3.13/3.14) e `publish.yml` (tag `v*` → build → PyPI Trusted Publishing OIDC → GH release, `--prerelease` para rc).

## Passos ordenados de implementação

1. Branch `feat/v1-rewrite`; deletar código antigo (src antigos, testes antigos, docs/api antigos; limpar `.coverage`/`htmlcov` do git).
2. Config primeiro: pyproject (versão, deps, taskipy, mypy) + pytest.ini — para cada passo seguinte ser verificável.
3. `core/` + testes (Success/Failure/match, Unit, Nil).
4. `errors/` + testes; depois `tests/helpers/` (test_errors, assertions).
5. `parameters/` + testes.
6. `datasources/` + testes (valida config pytest-asyncio).
7. `repositories/` + testes (map_error, cancelamento).
8. `usecases/` + testes (maior passo: executor → base → call_data).
9. `__init__.py` público + smoke test importando tudo da raiz.
10. `samples/` (container → check_connection → fibonacci → sales_report → main.py).
11. Docs: README, CHANGELOG, mkdocs.
12. CI workflows + `uv lock` + passada final completa.

## Verificação

Após cada passo e no final:
- `uv sync` → `uv run pytest` (cobertura ~100% no src, como hoje)
- `uv run mypy src tests samples` (strict, zero erros)
- `uv run python samples/main.py` (as 3 features rodam: sucesso, erro de negócio, background+monitor)
- `uv build` (wheel só com src, py.typed incluso)
- `uv run mkdocs build --strict`

## Referências abertas durante a implementação

- `C:\PROJETOS\C#\PACKAGES\return-success-or-error\src\ReturnSuccessOrError\Usecases\UsecaseExecutorBase.cs` (semântica de orquestração — a parte mais delicada)
- `C:\PROJETOS\C#\PACKAGES\return-success-or-error\src\ReturnSuccessOrError\Repositories\RepositoryBase.cs`
- `C:\PROJETOS\C#\PACKAGES\return-success-or-error\samples\` (padrão de composição a replicar)
- `C:\PROJETOS\C#\PACKAGES\return-success-or-error\README.md` (estrutura a espelhar)
