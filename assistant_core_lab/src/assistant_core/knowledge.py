"""Typed office and handbook knowledge sources loaded from CSV and JSON."""

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]) -> None:
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        try:
            with path.open(encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                required = {"name", "room", "hours"}
                if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                    raise DataError(f"office CSV must contain columns: {', '.join(sorted(required))}")
                rows = list(reader)
        except FileNotFoundError as exc:
            raise DataError(f"office file not found: {path}") from exc
        except (OSError, UnicodeError, csv.Error) as exc:
            raise DataError(f"could not read office file: {path}") from exc

        offices: dict[str, Office] = {}
        for line_number, row in enumerate(rows, start=2):
            if not all((row.get(key) or "").strip() for key in required):
                raise DataError(f"office record at line {line_number} is missing a required value")
            office = Office(row["name"].strip(), row["room"].strip(), row["hours"].strip())
            offices[office.name.lower()] = office
        return cls(offices)

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        lowered = text.lower()
        return next((office for name, office in self._offices.items() if name in lowered), None)


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class Handbook:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        try:
            with path.open(encoding="utf-8") as file:
                data: Any = json.load(file)
        except FileNotFoundError as exc:
            raise DataError(f"handbook file not found: {path}") from exc
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise DataError(f"could not read handbook file: {path}") from exc

        if not isinstance(data, list):
            raise DataError("handbook JSON must contain a list of rules")
        rules: list[Rule] = []
        for index, item in enumerate(data):
            if not isinstance(item, dict) or not all(item.get(key) for key in ("id", "title", "text")):
                raise DataError(f"handbook rule at index {index} must include id, title, and text")
            rules.append(Rule(str(item["id"]), str(item["title"]), str(item["text"])))
        return cls(rules)

    def search(self, query: str) -> Rule | None:
        words = [word for word in query.lower().split() if len(word) > 3]
        best_rule: Rule | None = None
        best_score = 0
        for rule in self._rules:
            rule_text = rule.text.lower()
            score = sum(word in rule_text for word in words)
            if score > best_score:
                best_rule = rule
                best_score = score
        return best_rule
