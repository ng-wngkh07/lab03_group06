"""Pure deterministic tuition parsing and calculation functions."""

import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    """Extract regular and retake credits from a tuition question."""
    retake_match = re.search(r"(\d+)\s*retake", text, flags=re.IGNORECASE)
    numbers = [int(number) for number in re.findall(r"\d+", text)]
    retake_credits = int(retake_match.group(1)) if retake_match else 0
    regular_numbers = numbers.copy()
    if retake_match:
        regular_numbers.remove(retake_credits)
    if not regular_numbers:
        raise InvalidRequest("How many credits?")
    return regular_numbers[0], retake_credits


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    """Calculate total tuition in VND without I/O or mutable state."""
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")
    if retake < 0:
        raise InvalidRequest("Retake credits cannot be negative.")
    return int(credits * rate + retake * rate * retake_multiplier)
