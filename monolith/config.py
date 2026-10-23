import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)

    if raw is None:
        return default

    return raw.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Settings:
    api_key: Optional[str]
    model: str
    rate: int
    retake_rate: float
    debug: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_key=os.getenv("API_KEY"),
            model=os.getenv(
                "MODEL",
                "gpt-small",
            ),
            rate=int(
                os.getenv(
                    "RATE",
                    "450000",
                )
            ),
            retake_rate=float(
                os.getenv(
                    "RETAKE_RATE",
                    "1.5",
                )
            ),
            debug=_env_bool(
                "DEBUG",
                True,
            ),
        )