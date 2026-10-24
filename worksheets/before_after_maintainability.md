# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | In `assistant_monolith.py`, line 16 (`RATE = 450000`) — 1 constant hard-coded in code | In `.env`, 1 variable (`CREDIT_RATE_VND=450000`) without editing or redeploying code |
| Can you run the tests without internet or an API key? | No (`llm()` uses `random.random()` causing 5% flakiness and simulated remote calls) | Yes (100% deterministic pure functions and `StubLLMResponder` / `TemplateResponder` running offline) |
| What happens if `handbook.json` is missing? | Prints `Warning: could not load handbook` and continues silently (`except:` in `load()`) | Raises `DataError` at startup, failing fast with an informative error message |
| Is any secret printed or logged? | Yes (`API_KEY = "sk-test-..."` printed in debug log in `llm()`) | No (`llm_api_key` has `repr=False`, excluded from logs, `.env` gitignored) |
| How long does it take a new teammate to find the fee logic? | Several minutes hunting through a ~65-line monolithic `handle()` function | A few seconds: clearly separated in `src/assistant_core/tools.py` (`parse_credits` and `tuition`) |
| Number of global variables | 9 (3 mutable: `history`, `offices`, `handbook`; 6 constants) | 0 (all state encapsulated in classes and injected via Dependency Injection) |
| Number of bare `except:` blocks | 3 (in `load()` and `main()`) | 0 (specific exception handling conforming to Ruff `BLE001`) |
| Lines in the longest function | ~65 lines (`handle()` in monolith) | ~15 lines (`AssistantService.handle()`) |
| `ruff check` issues | Multiple critical violations (bare except, wildcard/unsorted, formatting, unused state) | 0 issues (`All checks passed!` including `--select BLE`) |
| Can you swap the LLM without touching the service? | No (coupled directly to simulated `llm()` function inside `handle()`) | Yes (`Responder` Protocol adapter pattern decouples provider implementations from `AssistantService`) |

**Three sentences:**
1. **What improved most:** The architecture achieves clean separation of concerns and Twelve-Factor compliance, where tuition calculations are pure and deterministic, secrets are never exposed, and tests run fully offline in 0.04s.
2. **What got more complex:** The number of files and abstractions increased (from 1 monolithic script to 10 cohesive modules, Pydantic data schemas, and the `Responder` Protocol adapter pattern).
3. **What you would still change:** Add fuzzy/semantic search retrieval with vector embeddings for the student handbook, and integrate an OpenAPI/FastAPI web interface in Lab 4.
