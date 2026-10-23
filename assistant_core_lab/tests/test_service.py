"""Service contract, knowledge sources, and provider fallback behavior."""

from pydantic import ValidationError
import pytest

from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder


def test_message_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        Message(text="")


def test_greeting(service) -> None:
    response = service.handle(Message(text="hi"))
    assert response.intent is Intent.GREETING
    assert response.answer.startswith("Hello!")


def test_tuition_characterization(service) -> None:
    response = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert response.answer == "Your tuition is 9,450,000 VND."
    assert response.intent is Intent.FEE


def test_office_lookup_includes_source(service) -> None:
    response = service.handle(Message(text="where is the library?"))
    assert response.intent is Intent.OFFICE
    assert response.sources[0].title == "Library"


def test_provider_failure_uses_degraded_fallback(service) -> None:
    service.responder = StubLLMResponder(fail=True)
    response = service.handle(Message(text="thesis registration credits"))
    assert response.degraded
    assert response.sources
    assert "Thesis registration" in response.answer


def test_unknown_handbook_query(service) -> None:
    response = service.handle(Message(text="quasar nebula zirconium"))
    assert response.intent is Intent.UNKNOWN
    assert not response.sources
