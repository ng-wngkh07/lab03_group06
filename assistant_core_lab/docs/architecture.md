# Architecture: `assistant_core`

## 1. Module Table

| Module | Responsibility |
| :--- | :--- |
| `config.py` | Read settings from environment variables and `.env`; validate required keys and fallback defaults. |
| `errors.py` | Named domain exception hierarchy (`AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError`). |
| `models.py` | Public data contract: `Message`, `Response`, `Intent`, `Source` defined with Pydantic. |
| `router.py` | Choose an `Intent` from input text using lightweight, deterministic rules. |
| `knowledge.py` | Encapsulate office directory (CSV) and student handbook (JSON) knowledge sources and retrieval. |
| `tools.py` | Pure, deterministic utility functions (credit parsing and tuition calculation). |
| `responder.py` | Response generation behind a unified `Responder` Protocol (Template fallback and Stub LLM adapter). |
| `service.py` | `AssistantService.handle(msg: Message) -> Response` — the single entry point orchestrating routing, tools, knowledge, and responders. |
| `logging_setup.py` | Structured JSON log formatter routing structured events to `sys.stderr`. |
| `__main__.py` | Command-line interface accepting queries, logging telemetry, and printing answers to `sys.stdout`. |

## 2. Service Interface

The service exposes a single unified method:
```python
AssistantService.handle(msg: Message) -> Response
```

- **Input (`Message`)**:
  - `text`: Validated non-empty string between 1 and 2,000 characters.
  - `session_id`: Session identifier (defaults to `"local"`).
- **Output (`Response`)**:
  - `answer`: Text response to present to the user.
  - `intent`: Classified intent enum (`GREETING`, `FEE`, `OFFICE`, `RULE`, `UNKNOWN`).
  - `sources`: List of citations (`Source(id, title)`), non-empty when referencing handbook rules.
  - `degraded`: Boolean flag (`True` if a fallback or degraded calculation path was used).
- **Error Boundary Contract**:
  - Invalid user input is rejected early at the boundary with `ValidationError`.
  - Startup errors in settings or missing data files raise `ConfigError` or `DataError`.
  - Upstream provider failures (e.g., `ProviderError` from an LLM timeout) are caught internally; the service degrades gracefully using `TemplateResponder` without leaking exceptions or secrets to the caller.

## 3. Key Architectural Decisions

1. **Deterministic Tools for Arithmetic Calculations (`tools.py`)**:
   - *Decision*: Tuition calculation and credit parsing are pure mathematical functions in `tools.py`, never delegated to a language model.
   - *Reason*: Financial calculations require 100% exactness and zero hallucination. Pure functions have no side effects, no I/O, and are trivial to test deterministically across boundary conditions.

2. **Adapter Pattern for LLM Provider (`responder.py`)**:
   - *Decision*: The LLM interaction is abstracted behind the `Responder` Protocol with `TemplateResponder` and `StubLLMResponder` implementations.
   - *Reason*: Unit tests and CI/CD pipelines run entirely offline without API keys or network flakiness. Swapping between stubs, offline templates, and real LLMs (e.g., in Week 4) requires no modifications to `AssistantService`.

3. **Externalized Configuration (12-Factor III) & Secret Protection (`config.py`)**:
   - *Decision*: All configurations and credentials load from environment variables and `.env`, with `.env.example` committed to version control and `.env` strictly ignored by `.gitignore`. The `llm_api_key` attribute uses `Field(repr=False)`.
   - *Reason*: Eliminates hard-coded credentials and prevents accidental secret leakage in logs, stack traces, or Git commits while enabling clean environment-specific deployments.
