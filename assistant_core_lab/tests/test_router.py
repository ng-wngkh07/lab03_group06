"""Rule-based intent routing tests."""

import pytest

from assistant_core.models import Intent
from assistant_core.router import route


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello!", Intent.GREETING),
        ("tuition for 18 credits", Intent.FEE),
        ("where is the library?", Intent.OFFICE),
        ("can I register my thesis", Intent.RULE),
    ],
)
def test_routes_messages(text: str, expected: Intent) -> None:
    assert route(text, {"library"}) is expected
