"""Environment-based configuration loading and validation."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"
    llm_provider: str = "stub"
    llm_api_key: str | None = Field(default=None, repr=False)
    credit_rate_vnd: int = Field(default=450_000, ge=0)
    retake_multiplier: float = Field(default=1.5, ge=0)
    max_credits: int = Field(default=30, ge=1)
    log_level: str = "INFO"


def load_settings(env_file: str | None = ".env") -> Settings:
    """Read and validate settings; environment variables take precedence over .env."""
    if env_file:
        load_dotenv(env_file, override=False)

    try:
        settings = Settings(
            data_dir=Path(os.getenv("ASSISTANT_DATA_DIR", str(Path(__file__).resolve().parents[2] / "data"))),
            llm_provider=os.getenv("LLM_PROVIDER", "stub").strip().lower(),
            llm_api_key=os.getenv("LLM_API_KEY") or None,
            credit_rate_vnd=os.getenv("CREDIT_RATE_VND", "450000"),
            retake_multiplier=os.getenv("RETAKE_MULTIPLIER", "1.5"),
            max_credits=os.getenv("MAX_CREDITS", "30"),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        )
    except (PydanticValidationError, ValueError) as exc:
        raise ConfigError(f"Invalid assistant configuration: {exc}") from exc

    if settings.llm_provider not in {"stub", "template"} and not settings.llm_api_key:
        raise ConfigError(f"LLM_API_KEY is required when LLM_PROVIDER={settings.llm_provider!r}")
    if settings.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
    return settings
