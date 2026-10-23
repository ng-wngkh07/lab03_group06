"""Shared offline fixtures for the assistant service tests."""

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def service() -> AssistantService:
    settings = Settings(data_dir=PROJECT_ROOT / "data")
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    return AssistantService(settings, offices, handbook, StubLLMResponder())
