"""Tuition tools are pure and deterministic."""

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake() -> None:
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_tuition_characterization_value() -> None:
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


@pytest.mark.parametrize("credits", [0, 31])
def test_tuition_rejects_out_of_range_credits(credits: int) -> None:
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)


def test_parse_missing_credits() -> None:
    with pytest.raises(InvalidRequest, match="How many credits"):
        parse_credits("tuition fee")
