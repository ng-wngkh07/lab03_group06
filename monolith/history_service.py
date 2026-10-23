import logging

from pathlib import Path
from typing import Iterable


logger = logging.getLogger(__name__)


def save_history(
    path: Path,
    history: Iterable[str],
) -> None:
    items = list(history)

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for item in items:
            file.write(
                item + "\n"
            )

    logger.debug(
        "Saved %d lines to %s",
        len(items),
        path,
    )


def build_stats(
    history: Iterable[str],
    office_keys: Iterable[str],
) -> str:
    keys = tuple(office_keys)

    counts = {
        "fee": 0,
        "office": 0,
        "rule": 0,
        "other": 0,
    }

    for item in history:
        message = item.lower()

        if (
            "fee" in message
            or "tuition" in message
        ):
            counts["fee"] += 1

        elif any(
            key in message
            for key in keys
        ):
            counts["office"] += 1

        elif any(
            word in message
            for word in (
                "thesis",
                "retake",
                "exam",
                "credit",
            )
        ):
            counts["rule"] += 1

        else:
            counts["other"] += 1

    return (
        f"fee={counts['fee']} "
        f"office={counts['office']} "
        f"rule={counts['rule']} "
        f"other={counts['other']}"
    )