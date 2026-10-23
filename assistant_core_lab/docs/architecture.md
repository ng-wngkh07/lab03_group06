# Assistant Core Architecture

## Module responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Read settings from the environment and validate provider credentials, rates, credit limits, data path, and log level. The API key is excluded from the settings representation. |
| `errors.py` | Define named assistant, configuration, data, request-validation, and provider errors. |
| `models.py` | Define the typed public contracts `Message`, `Response`, `Intent`, and `Source`. Message text is limited to 1-2000 characters. |
| `router.py` | Choose an intent using simple deterministic rules for greetings, fees, and office names; other questions are sent to handbook search. |
| `knowledge.py` | Load and validate the office CSV and handbook JSON, then expose office lookup and handbook keyword search. Missing or malformed data raises `DataError` during startup. |
| `tools.py` | Parse credit counts and calculate tuition with deterministic pure functions. No provider or file I/O is used. |
| `responder.py` | Define the response-generation protocol and provide template and injectable stub implementations. Provider errors use a named `ProviderError`. |
| `service.py` | Compose dependencies and expose `AssistantService.handle(Message) -> Response` as the sole application entry point. It handles provider fallback and marks degraded responses. |
| `logging_setup.py` | Configure JSON logs on stderr with an allowlist of operational fields. User messages and credentials are not logged. |
| `__main__.py` | Build the service, accept command-line or interactive input, call `handle`, and print answers to stdout. |

## Service interface

All clients use `AssistantService.handle(msg: Message) -> Response`.

- `Message` contains `text` (1-2000 characters) and `session_id` (defaults to `local`). Pydantic rejects invalid message data at construction.
- `Response` contains `answer`, `intent`, `sources`, and `degraded`.
- Invalid fee details raise `InvalidRequest`, a named request-validation error. Invalid environment configuration raises `ConfigError`; missing or malformed startup data raises `DataError`.
- A `ProviderError` is caught by the service. It returns a template answer with the matched source and `degraded=True`; provider-specific failures do not reach callers.
- The CLI, a future FastAPI backend, and a future UI can share the same method without depending on terminal behavior.

## Design decisions

1. **Tuition stays in `tools.py` and never uses an LLM.** Rates and credit limits make this a deterministic calculation that is easy to test and cannot be varied by generated text.
2. **The provider sits behind `Responder`, with a template fallback.** The stub works offline and can simulate a failure, while dependency injection lets the service be tested and a future provider be swapped without changing service orchestration.
3. **Configuration comes from the environment and logs use an allowlist.** `.env.example` documents every supported setting; `.env` is ignored, the API key uses `repr=False`, and the JSON formatter excludes prompts and secrets.

## Scope note

The original monolith also has `history`, `stats`, and `save` commands. The Lab 3 target contract does not define their persistence or privacy behavior, so they are not carried into this service skeleton. They can be added as a separately specified feature without placing file or history responsibilities in the request service.
