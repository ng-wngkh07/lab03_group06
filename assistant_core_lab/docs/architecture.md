# Architecture: `assistant_core`

## 1. Module Table (Part B.1)

| Module | Responsibility |
| :--- | :--- |
| `config.py` | Read settings from environment variables and `.env`; validate required keys, defaults, and prevent secret exposure. |
| `errors.py` | Domain exception hierarchy (`AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError`). |
| `models.py` | Public data schemas (`Message`, `Response`, `Intent`, `Source`) validated using Pydantic. |
| `router.py` | Deterministic intent classification (`GREETING`, `FEE`, `OFFICE`, `RULE`, `UNKNOWN`) from input text. |
| `knowledge.py` | Knowledge store management for office directory (`offices.csv`) and student handbook (`handbook.json`). |
| `tools.py` | Pure, deterministic utility functions for credit parsing and tuition fee calculation. |
| `responder.py` | Unified `Responder` Protocol interface with `TemplateResponder` fallback and `StubLLMResponder` adapter. |
| `service.py` | `AssistantService.handle(msg: Message) -> Response` orchestrator connecting routing, tools, knowledge, and responders. |
| `logging_setup.py` | Structured JSON log formatter routing operational telemetry to `sys.stderr`. |
| `__main__.py` | CLI entry point parsing command-line queries, running the service, and emitting answers to `sys.stdout`. |

## 2. Service Interface (Part B.2)

The service exposes a single, unified entry point:
```python
AssistantService.handle(msg: Message) -> Response
```

### Input Contract (`Message`)
- `text`: Non-empty string between 1 and 2,000 characters. Stripped and validated by Pydantic.
- `session_id`: Optional session tracking string (defaults to `"local"`).

### Output Contract (`Response`)
- `answer`: Text response to present to the user.
- `intent`: Classified intent enum (`GREETING`, `FEE`, `OFFICE`, `RULE`, `UNKNOWN`).
- `sources`: List of citations (`Source(id, title)`), non-empty when referencing handbook rules.
- `degraded`: Boolean flag (`True` if a fallback or degraded calculation path was used).

### Error Boundary Contract
- **Input Validation**: Malformed or empty messages fail early at the boundary with `ValidationError`.
- **System Startup**: Missing configuration or corrupt data files raise explicit `ConfigError` or `DataError`.
- **Graceful Degradation**: Upstream provider failures (`ProviderError` e.g. LLM timeout or unreachability) are caught internally. The service falls back to `TemplateResponder` with `degraded=True` without leaking stack traces or unhandled exceptions to the caller.

## 3. Key Architectural Decisions

1. **Fees are computed in `tools.py`, never by an LLM (exact, testable)**:
   - *Decision*: Tuition calculation (`tuition`) and credit parsing (`parse_credits`) are implemented as pure, deterministic mathematical functions in `tools.py`, never delegated to an LLM.
   - *Reason*: Financial computations require 100% exactness and zero hallucination. Pure functions have no side effects, no I/O, and are trivial to test deterministically across boundary conditions (0 credits, max limits, retake multipliers).

2. **The LLM sits behind `Responder`; stub needs no key, so tests and CI run offline**:
   - *Decision*: All LLM interaction is decoupled behind the `Responder` Protocol, implemented by `TemplateResponder` and `StubLLMResponder`.
   - *Reason*: Unit tests and CI/CD pipelines run entirely offline with zero latency, zero flaky network dependencies, and no paid API quotas or keys. In future iterations, production LLM adapters (OpenAI, Claude, Ollama) can be swapped in without modifying `AssistantService`.

3. **Configuration comes from the environment; `.env.example` documents every variable**:
   - *Decision*: All system parameters and credentials load from environment variables and `.env` (following Twelve-Factor App Factor III). `.env.example` documents every variable with safe defaults. Secrets (`llm_api_key`) use `Field(repr=False)` and `.env` is strictly gitignored.
   - *Reason*: Eliminates hardcoded secrets and configuration from code, preventing credential leakage in logs or git commits, while making environment setup reproducible for new teammates and CI runners.
