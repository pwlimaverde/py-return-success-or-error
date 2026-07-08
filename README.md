<img src="https://py-return-success-or-error.readthedocs.io/pt-br/latest/assets/logo.png" width="200" height="200">

# py-return-success-or-error

Result/Either com **erro fechado por feature** para Clean Architecture em Python: `DataSource → Repository → Usecase`, async-first, tipagem estrita e **zero dependências**.

> Versão irmã da lib C# [ReturnSuccessOrError](https://github.com/pwlimaverde/return-success-or-error) — mesma filosofia, mesmo desenho de camadas, mesma estratégia de composição.

## O problema

Exceções são ótimas para falhas técnicas, mas péssimas como contrato de domínio: o chamador não sabe quais falhas pode receber, nada o obriga a tratá-las, e o "catch genérico" espalha `except Exception` pelo código. E um Result com erro universal (um `AppError` fixo para tudo) resolve só metade: o chamador continua sem saber **quais** erros aquela feature pode produzir.

## A solução por design

Cada feature declara o seu **conjunto fechado de erros** — uma união de tipos concretos — e o resultado é parametrizado nesse conjunto:

```python
type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric

result: ReturnSuccessOrError[str, CheckConnectionError]
```

O consumo é **exaustivo**: com `match/case` + `assert_never`, o mypy/pyright prova em tempo de checagem que nenhum caso ficou sem tratamento — o análogo Python da exaustividade do compilador C# sobre uma `union`.

As falhas têm três origens, todas convergindo para a união fechada:

| Origem | Onde é tratada |
|---|---|
| Regra de negócio | `process` → `self.fail(caso)` |
| Falha técnica de I/O | `RepositoryBase.map_error(exception, params)` (abstrato) |
| Bug inesperado | `UsecaseExecutorBase.on_unexpected(exception)` (abstrato) |

O **cancelamento** é a exceção do contrato: `asyncio.CancelledError` nunca vira `Failure` — propaga como exceção, no idioma do asyncio.

## Instalação

```bash
pip install py-return-success-or-error
# ou
uv add py-return-success-or-error
```

Requer Python **>= 3.13**. Recomenda-se rodar mypy/pyright em modo estrito — a exaustividade é uma feature de tipagem.

## Início rápido em 5 passos

### 1. Declare a união fechada de erros da feature

```python
from dataclasses import dataclass
from py_return_success_or_error import AppError, ErrorGeneric

@dataclass(frozen=True)
class Offline(AppError):
    """Sem conectividade."""

@dataclass(frozen=True)
class ConnectionTimeout(AppError):
    """A verificação excedeu o tempo limite."""

type CheckConnectionError = Offline | ConnectionTimeout | ErrorGeneric
```

Herdar de `AppError` é conveniência (dá `message`, igualdade por valor e `with_message`), não obrigação — `TError` pode ser qualquer tipo.

### 2. Declare os parâmetros (só dados)

```python
from py_return_success_or_error import NO_PARAMS, NoParams, Parameters

# sem entrada? use NO_PARAMS. Com entrada:
@dataclass(frozen=True)
class BuscaClienteParameters(Parameters):
    cliente_id: int
```

### 3. Implemente o DataSource (porta "burra")

Devolve o dado bruto ou **lança** a exceção técnica original. Não conhece o domínio.

```python
from py_return_success_or_error import DataSource

class PingDataSource(DataSource[bool, NoParams]):
    async def __call__(self, parameters: NoParams) -> bool:
        return await self._client.ping()  # pode lançar TimeoutError etc.
```

### 4. Implemente o Repository (camada anticorrupção)

Traduz cada exceção técnica num caso da união fechada — o try/except mora **aqui**, uma única vez.

```python
from py_return_success_or_error import RepositoryBase

class CheckConnectionRepository(
    RepositoryBase[bool, NoParams, CheckConnectionError]
):
    def map_error(
        self, exception: Exception, parameters: NoParams
    ) -> CheckConnectionError:
        match exception:
            case TimeoutError():
                return ConnectionTimeout(message=str(exception))
            case _:
                return ErrorGeneric(message=str(exception))
```

### 5. Implemente o Usecase e consuma

```python
from py_return_success_or_error import (
    Failure, ReturnSuccessOrError, Success, UsecaseBaseCallData,
)
from typing import assert_never

class CheckConnectionUsecase(
    UsecaseBaseCallData[str, bool, NoParams, CheckConnectionError]
):
    def process(
        self, data: bool, parameters: NoParams
    ) -> ReturnSuccessOrError[str, CheckConnectionError]:
        if not data:
            return self.fail(Offline(message='sem acesso à rede'))
        return self.ok('Conectado')

    def on_unexpected(self, exception: Exception) -> CheckConnectionError:
        return ErrorGeneric(message=str(exception))


result = await CheckConnectionUsecase(repository)(NO_PARAMS)
match result:
    case Success(mensagem):
        print(mensagem)
    case Failure(error):
        match error:
            case Offline():
                ...  # cada caso tratado
            case ConnectionTimeout():
                ...
            case ErrorGeneric():
                ...
            case _:
                assert_never(error)  # o mypy prova a cobertura
    case _:
        assert_never(result)
```

## Conceitos centrais

| Tipo | Papel |
|---|---|
| `ReturnSuccessOrError[TValue, TError]` | União fechada `Success \| Failure` — o contrato de retorno |
| `Success[TValue]` / `Failure[TError]` | Casos imutáveis com igualdade por valor |
| `match(result, on_success=..., on_error=...)` | Consumo funcional (≙ `Match` do C#) |
| `Unit` / `UNIT` | Operação sem valor de retorno (`ReturnSuccessOrError[Unit, E]`) |
| `Nil` / `NIL` | Nulo como resultado **válido** (`ReturnSuccessOrError[Cliente \| Nil, E]`) |
| `AppError` | Base opcional de erros: valor imutável, `message`, `with_message()` |
| `ErrorGeneric` | Caso pronto para o "inesperado" |
| `Parameters` / `NoParams` / `NO_PARAMS` | Entrada das camadas — só dados |
| `DataSource[TData, TParams]` | Porta burra: dado bruto ou exceção |
| `Repository` / `RepositoryBase` | Anticorrupção: exceção → `map_error` → `Failure` |
| `UsecaseBase` | Regra pura, sem dados externos |
| `UsecaseBaseCallData` | FETCH → CURTO-CIRCUITO → PROCESS |

## Fluxo de execução

```
await usecase(parameters)
  └─ _measured (opcional: monitor_execution_time)
       └─ FETCH:  await repository(parameters)
            ├─ exceção técnica ──→ map_error ──→ Failure  ─┐
            └─ dado bruto ──→ Success                      │
       └─ CURTO-CIRCUITO: Failure do fetch retorna direto ◄┘  (process NÃO roda)
       └─ PROCESS: process(data, parameters)   [síncrono, CPU-bound]
            ├─ regra ok    ──→ self.ok(valor)   ──→ Success
            ├─ regra falha ──→ self.fail(caso)  ──→ Failure
            └─ bug         ──→ on_unexpected    ──→ Failure
                (asyncio.CancelledError sempre propaga)
```

- `run_in_background=True` despacha o `process` para fora do event loop via `_dispatch_to_background` (padrão: `asyncio.to_thread`, ≙ `Task.Run`), mantendo o loop responsivo. No build padrão do CPython o GIL limita o paralelismo de CPU puro — no **free-threaded (3.14+, PEP 779)** o paralelismo é real. Uma thread já iniciada não é interrompida pelo cancelamento. Precisa de mais? `_dispatch_to_background` é **sobrescrevível** — plugue um `InterpreterPoolExecutor` (3.14+, PEP 734) ou `ProcessPoolExecutor`:

```python
class MeuUsecase(FibonacciUsecase):
    _executor = InterpreterPoolExecutor(max_workers=4)  # Python 3.14+

    async def _dispatch_to_background(self, run):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, run)
```
- `monitor_execution_time=True` mede a execução e chama `on_execution_time_measured(elapsed)` — o padrão loga em DEBUG; sobrescreva para integrar à sua observabilidade.

## Estrutura de código recomendada (por feature)

```
minha_app/
├── composition/
│   ├── container.py              # o container QUE VOCÊ escolher (ou wiring manual)
│   └── feature_registration.py   # add_features(container) — agregador fino
└── features/
    └── check_connection/
        ├── errors.py             # casos concretos + união fechada
        ├── datasources.py        # portas burras
        ├── repositories.py       # map_error
        ├── usecases.py           # process + on_unexpected
        ├── services.py           # fachada consumida pela UI/API
        └── register.py           # add_check_connection_feature(container)
```

## Composição e orquestração (DI fora do core)

**A biblioteca não contém nenhum tipo de composição/DI** — nem marker interface, nem container, nem registro. Isso a mantém com zero dependências e agnóstica de framework. A composição é uma **convenção do consumidor**, em três camadas:

**A) Service facade por feature** — o ponto único que a UI/API consome:

```python
class CheckConnectionService:
    def __init__(self, usecase: CheckConnectionUsecase) -> None:
        self._usecase = usecase

    async def check(self) -> ReturnSuccessOrError[str, CheckConnectionError]:
        return await self._usecase(NO_PARAMS)
```

**B) Função de registro por feature** — registra datasource, repository, usecase e service:

```python
def add_check_connection_feature(container: Container) -> Container:
    return (
        container
        .add_singleton(PingDataSource, lambda _: PingDataSource())
        .add_singleton(
            CheckConnectionRepository,
            lambda c: CheckConnectionRepository(c.resolve(PingDataSource)),
        )
        .add_singleton(
            CheckConnectionUsecase,
            lambda c: CheckConnectionUsecase(c.resolve(CheckConnectionRepository)),
        )
        .add_singleton(
            CheckConnectionService,
            lambda c: CheckConnectionService(c.resolve(CheckConnectionUsecase)),
        )
    )
```

**C) Agregador fino** — adicionar uma feature ao app = uma linha:

```python
def add_features(container: Container) -> Container:
    add_check_connection_feature(container)
    add_fibonacci_feature(container)
    add_sales_report_feature(container)
    return container
```

O container do exemplo tem ~30 linhas (veja `samples/composition/container.py`). Com `dependency-injector`, `punq` ou wiring manual por construtores, a convenção é a mesma — a lib não sabe e não precisa saber qual você usa. O diretório [`samples/`](samples/) traz três features completas e executáveis (`uv run task samples`).

## Cancelamento (asyncio)

Não há parâmetro de cancellation token: o cancelamento asyncio é **ambiente**. Um `asyncio.CancelledError` pode emergir de qualquer `await` e **sempre propaga** — nunca passa por `map_error` nem `on_unexpected`, porque cancelamento não é falha de domínio. Um cancelamento já pendente é entregue **antes** do `process` rodar, tanto no modo direto quanto em background.

## Exaustividade com match/assert_never

A tipagem substitui a prova do compilador C#. O idioma canônico:

```python
match error:
    case Offline():
        ...
    case ConnectionTimeout():
        ...
    case ErrorGeneric():
        ...
    case _:
        assert_never(error)
```

Se alguém adicionar um caso à união e esquecer de tratá-lo, o **mypy acusa o erro** no `assert_never`. Configure `[tool.mypy] strict = true` (ou pyright `strict`) no seu projeto.

## Portabilidade

O usecase depende da abstração `Repository`; o repository depende da abstração `DataSource`. Trocar a fonte (HTTP → arquivo → memória) = trocar a fábrica do datasource no registro da feature — nenhuma outra linha muda. Veja a feature `sales_report` nos samples, que roda com fonte CSV ou em memória.

## Migração da versão 0.x

A 1.0.0 é uma reescrita completa (breaking). Mapa de migração:

| 0.x | 1.0 |
|---|---|
| `SuccessReturn(valor)` | `Success(valor)` / `self.ok(valor)` |
| `ErrorReturn(erro)` | `Failure(erro)` / `self.fail(erro)` |
| `ReturnSuccessOrError[T]` (erro fixo `AppError`) | `ReturnSuccessOrError[TValue, TError]` (erro por feature) |
| `AppError` (dataclass + `Exception`) | `AppError` (valor imutável, sem `Exception`) |
| `ParametersReturnResult` com campo `error` | `Parameters` — só dados |
| `Datasource.__call__` síncrono | `DataSource.__call__` **async** |
| `RepositoryMixin._resultDatasource` (erro fixo dos params) | `RepositoryBase.map_error(exception, params)` |
| `UsecaseBase(parameters)` síncrono | `await usecase(parameters)` |
| `ThreadMixin.runNewThread` | `run_in_background=True` |
| `EMPTY` / `Empty` | `UNIT` (sem retorno) ou `NIL` (nulo válido) |

## Licença

MIT — veja [LICENSE](LICENSE).
