import logging
import time

from typing import Callable


logger = logging.getLogger(__name__)


class LLMTimeoutError(Exception):
    pass


def ask_llm(
    prompt: str,
    model: str,
    rng: Callable[[], float],
) -> str:
    logger.debug(
        "Calling model %s with prompt: %s",
        model,
        prompt[:60],
    )

    time.sleep(0.2)

    if rng() < 0.1:
        raise LLMTimeoutError(
            "LLM timeout"
        )

    return (
        "Here is what I found: "
        + prompt[-120:]
    )