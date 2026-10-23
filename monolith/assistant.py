import logging
import random

from pathlib import Path

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from config import BASE_DIR
from config import Settings

from fee_service import handle_fee

from handbook_service import (
    find_best_rule,
)

from history_service import (
    build_stats,
    save_history,
)

from llm_service import (
    LLMTimeoutError,
    ask_llm,
)

from models import Response
from models import Status

from office_service import find_office


logger = logging.getLogger(__name__)


class Assistant:
    def __init__(
        self,
        settings: Settings,
        offices: Dict[str, List[str]],
        handbook: List[Dict[str, Any]],
        rng: Optional[
            Callable[[], float]
        ] = None,
        base_dir: Path = BASE_DIR,
    ) -> None:
        self.settings = settings

        self.offices = offices
        self.handbook = handbook

        self.history: List[str] = []

        self.rng = (
            rng
            if rng is not None
            else random.random
        )

        self.base_dir = base_dir

    def handle(
        self,
        msg: str,
    ) -> Response:
        self.history.append(msg)

        message = (
            msg
            .lower()
            .strip()
        )

        if message == "":
            return Response(
                Status.EMPTY_INPUT,
                "empty",
            )

        if message in {
            "hi",
            "hello",
            "hey",
            "xin chao",
        }:
            return Response(
                Status.OK,
                (
                    "Hello! I can help with "
                    "offices, fees and rules."
                ),
            )

        if message == "history":
            return Response(
                Status.OK,
                "\n".join(
                    self.history
                ),
            )

        if message == "stats":
            return Response(
                Status.OK,
                build_stats(
                    self.history,
                    self.offices.keys(),
                ),
            )

        if message.startswith("save"):
            parts = message.split()

            raw_name = (
                parts[-1]
                if len(parts) > 1
                else "history.txt"
            )

            filename = Path(
                raw_name
            ).name

            try:
                save_history(
                    self.base_dir
                    / filename,
                    self.history,
                )

            except OSError as error:
                logger.error(
                    "Could not save history: %s",
                    error,
                )

                return Response(
                    Status.NOT_FOUND,
                    "could not save history",
                )

            return Response(
                Status.SAVED,
                "saved",
            )

        if (
            "fee" in message
            or "tuition" in message
        ):
            return handle_fee(
                message,
                self.settings.rate,
                self.settings.retake_rate,
            )

        office_response = find_office(
            message,
            self.offices,
        )

        if office_response is not None:
            return office_response

        rule = find_best_rule(
            message,
            self.handbook,
        )

        if rule is not None:
            rule_text = str(
                rule.get(
                    "text",
                    "",
                )
            )

            rule_id = str(
                rule.get(
                    "id",
                    "",
                )
            )

            try:
                answer = ask_llm(
                    (
                        "Answer using this rule: "
                        + rule_text
                        + " Question: "
                        + msg
                    ),
                    self.settings.model,
                    self.rng,
                )

                return Response(
                    Status.OK,
                    (
                        answer
                        + " (source: "
                        + rule_id
                        + ")"
                    ),
                )

            except LLMTimeoutError as error:
                logger.warning(
                    "LLM failed: %s",
                    error,
                )

                return Response(
                    Status.OK,
                    (
                        rule_text
                        + " (source: "
                        + rule_id
                        + ")"
                    ),
                )

        return Response(
            Status.NOT_FOUND,
            "Sorry I dont know",
        )