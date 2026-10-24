# Lab 3 — AI extension review

1. Ask an AI coding assistant to extend your service with ONE feature, e.g.
   "Add an 'exam absence' answer that tells students the deadline from the handbook."
2. Paste the prompt you used:
   `Add support for a 'help' intent that lists what the bot can do (office lookup, tuition calculation, and handbook rule search).`

3. Review the generated code manually. Document **at least three changes** you made:

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | AI directly added response formatting strings inside `router.py` | Violated Single Responsibility and the service interface boundary contract | Moved formatting to `AssistantService.handle()` returning a typed `Response`, keeping `router.py` purely focused on returning `Intent.HELP` | Preserves clean architecture (Route -> Service -> Responder) so API and CLI callers get identical typed responses |
| 2 | AI logged `logger.info(f"User asked: {msg.text}")` in the request flow | Logged raw user message text into system logs | Modified logging to record only operational metadata (`intent="help"`, `latency_ms`, `session`, `degraded=False`) | Prevents leaking sensitive user data or PII into logs, complying with the lab's privacy guidelines |
| 3 | AI included manual `print()` statements for testing in `__main__.py` | Tests were manual, unverified by CI, and output was not asserted | Added automated unit tests in `tests/test_router.py` and `tests/test_service.py` using `pytest` | Ensures automated test coverage in CI/CD without relying on human terminal inspection |

Checklist: interfaces respected? new dependencies? secrets? logging of user data? tests added and meaningful?
Record the use in `docs/ai-use-log.md`.
