import logging
import sys
import time

from assistant import Assistant

from config import BASE_DIR
from config import Settings

from data_loader import (
    load_handbook,
    load_offices,
)


def configure_logging(
    debug: bool,
) -> None:
    logging.basicConfig(
        level=(
            logging.DEBUG
            if debug
            else logging.INFO
        ),
        format=(
            "%(levelname)s: "
            "%(message)s"
        ),
    )


def build_assistant() -> Assistant:
    settings = Settings.from_env()

    configure_logging(
        settings.debug
    )

    offices = load_offices(
        BASE_DIR
        / "data"
        / "offices.csv"
    )

    handbook = load_handbook(
        BASE_DIR
        / "data"
        / "handbook.json"
    )

    return Assistant(
        settings=settings,
        offices=offices,
        handbook=handbook,
    )


def main() -> None:
    assistant = build_assistant()

    if len(sys.argv) > 1:
        response = assistant.handle(
            " ".join(
                sys.argv[1:]
            )
        )

        print(
            response.message
        )

        return

    print(
        "assistant ready"
    )

    while True:
        try:
            question = input(
                "> "
            )

        except (
            EOFError,
            KeyboardInterrupt,
        ):
            print()
            break

        if question == "quit":
            break

        start = time.time()

        response = assistant.handle(
            question
        )

        print(
            response.message
        )

        logging.debug(
            "Took %.2f seconds",
            time.time() - start,
        )


if __name__ == "__main__":
    main()