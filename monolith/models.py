from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    OK = "ok"
    EMPTY_INPUT = "empty_input"
    SAVED = "saved"
    MISSING_CREDITS = "missing_credits"
    TOO_MANY_CREDITS = "too_many_credits"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class Response:
    status: Status
    message: str