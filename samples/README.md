# Samples — organização por feature (Clean Architecture)

Três features executáveis que mostram o fluxo da lib —
`DataSource → Repository → Usecase → Service` — com **erro fechado por
feature** e composição/DI vivendo inteiramente fora do core.

## Estrutura

```text
samples/
├── main.py                        # ponto de entrada: resolve e roda as features
├── composition/                   # DI do app — fora do core da lib
│   ├── container.py               # container mínimo feito à mão (~30 linhas)
│   └── feature_registration.py    # agregador: 1 feature = 1 linha
└── features/
    └── <feature>/
        ├── __init__.py            # API pública da feature (re-exports)
        ├── register.py            # add_<feature>_feature(container)
        ├── domain/                # regras, contratos e tipos
        │   ├── errors.py          # união FECHADA de erros da feature
        │   ├── models.py          # modelos do domínio (quando há)
        │   ├── parameters.py      # parâmetros — só dados (quando há)
        │   ├── services.py        # CONTRATO do service (ABC)
        │   └── usecases.py        # casos de uso (process + on_unexpected)
        ├── datasources/           # portas de dados — 1 módulo por fonte
        ├── repositories/          # anticorrupção (map_error)
        └── services/              # implementação do contrato do service
```

## Regra de dependência

As setas apontam sempre para dentro (para o domínio):

```text
datasources ──▶ domain ◀── repositories ◀── services (impl)
                  ▲
        register.py (conhece as implementações; só ele)
```

- `domain/` **não importa** nenhuma camada externa — só a lib e a
  própria feature.
- `services/<feature>_service.py` implementa o contrato ABC de
  `domain/services.py`. O consumidor (a UI, o `main.py`) depende **só do
  contrato** e o resolve pelo container.
- `register.py` é o único módulo que conhece as implementações
  concretas — trocar a fonte de dados é trocar uma fábrica ali
  (portabilidade: veja `sales_report`, que roda com CSV ou memória).

## As três features

| Feature | O que demonstra | Camadas |
| --- | --- | --- |
| `check_connection` | união fechada de erros + `map_error` (timeout → `ConnectionTimeout`) | todas |
| `fibonacci` | `UsecaseBase` puro (sem I/O) com `run_in_background` + monitor de tempo | domain + services |
| `sales_report` | portabilidade (2 datasources), models e parameters no domínio | todas |

## Como adicionar uma feature

1. Crie `features/minha_feature/domain/` com `errors.py` (união
   fechada), `parameters.py`/`models.py` se houver dados,
   `services.py` (contrato ABC) e `usecases.py`.
2. Implemente as camadas externas necessárias: `datasources/`,
   `repositories/`, `services/` (a implementação do contrato).
3. Escreva `register.py` encadeando DataSource → Repository → UseCase →
   Service, registrando o **contrato** como chave.
4. Exponha a API pública no `__init__.py` da feature.
5. Adicione uma linha em `composition/feature_registration.py`.

## Executando

```bash
uv run task samples        # ou: uv run python samples/main.py
uv run task lint           # ruff em src, tests e samples
uv run task typecheck      # mypy --strict cobre os samples
```
