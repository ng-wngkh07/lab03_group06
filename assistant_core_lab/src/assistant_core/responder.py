"""Replaceable response-generation interface with offline implementations."""

from typing import Protocol

from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule


class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str:
        """Explain a matched handbook rule using the supplied question."""
        ...


class TemplateResponder:
    def explain(self, question: str, rule: Rule) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Offline stand-in for an LLM; failure can be injected in service tests."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"
