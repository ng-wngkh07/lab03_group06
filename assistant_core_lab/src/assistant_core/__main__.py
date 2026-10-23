"""Command-line adapter; all requests use AssistantService.handle."""

import argparse
import logging
import sys
from time import perf_counter

from pydantic import ValidationError as PydanticValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import AssistantError, ConfigError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import configure_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService


def build_service(settings: Settings) -> AssistantService:
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    if settings.llm_provider == "stub":
        responder = StubLLMResponder()
    elif settings.llm_provider == "template":
        responder = TemplateResponder()
    else:
        raise ConfigError(f"LLM provider {settings.llm_provider!r} is not implemented in Lab 3.")
    return AssistantService(settings, offices, handbook, responder)


def _answer(service: AssistantService, text: str, session_id: str) -> bool:
    try:
        msg = Message(text=text, session_id=session_id)
        started = perf_counter()
        response = service.handle(msg)
    except (PydanticValidationError, AssistantError) as exc:
        print(str(exc), file=sys.stderr)
        return False

    latency_ms = round((perf_counter() - started) * 1000, 1)
    logging.getLogger("assistant_core").info(
        "handled",
        extra={
            "intent": response.intent.value,
            "latency_ms": latency_ms,
            "session": session_id,
            "degraded": response.degraded,
        },
    )
    print(response.answer)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Student assistant")
    parser.add_argument("message", nargs="*", help="Question for the assistant")
    parser.add_argument("--session-id", default="local", help="Session identifier")
    parser.add_argument("--env-file", default=".env", help="Optional environment file")
    args = parser.parse_args()

    try:
        settings = load_settings(args.env_file)
        configure_logging(settings.log_level)
        service = build_service(settings)
    except AssistantError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc

    if args.message:
        _answer(service, " ".join(args.message), args.session_id)
        return

    print("assistant ready", file=sys.stderr)
    while True:
        try:
            question = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.strip().lower() == "quit":
            break
        _answer(service, question, args.session_id)


if __name__ == "__main__":
    main()
