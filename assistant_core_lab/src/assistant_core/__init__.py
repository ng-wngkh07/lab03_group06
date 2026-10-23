"""Maintainable student assistant service."""

from .models import Intent, Message, Response, Source
from .service import AssistantService

__all__ = ["AssistantService", "Intent", "Message", "Response", "Source"]
