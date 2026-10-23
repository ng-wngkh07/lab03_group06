import csv
import json
import logging

from pathlib import Path
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


def load_offices(
    path: Path,
) -> Dict[str, List[str]]:
    offices: Dict[str, List[str]] = {}

    try:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            next(reader, None)

            for row in reader:
                if len(row) < 3:
                    logger.warning(
                        "Skipping malformed office row: %r",
                        row,
                    )
                    continue

                offices[row[0].lower()] = row

    except (OSError, csv.Error) as error:
        logger.error(
            "Could not load offices: %s",
            error,
        )

    return offices


def load_handbook(
    path: Path,
) -> List[Dict[str, Any]]:
    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ) as error:
        logger.error(
            "Could not load handbook: %s",
            error,
        )

        return []

    if not isinstance(data, list):
        logger.error(
            "Handbook must contain a JSON list."
        )

        return []

    return data