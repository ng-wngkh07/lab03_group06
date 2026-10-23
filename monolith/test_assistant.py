import tempfile
import unittest

from pathlib import Path

from assistant import Assistant

from config import Settings

from models import Status


class AssistantTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.settings = Settings(
            api_key=None,
            model="gpt-small",
            rate=450000,
            retake_rate=1.5,
            debug=False,
        )

        self.offices = {
            "library": [
                "Library",
                "A101",
                "08:00-17:00",
            ],
        }

        self.handbook = [
            {
                "id": "RULE-1",
                "text": (
                    "Students may register "
                    "a thesis after "
                    "120 credits."
                ),
            }
        ]

    def make_assistant(
        self,
        rng=lambda: 0.5,
        base_dir=None,
    ) -> Assistant:
        if base_dir is None:
            base_dir = Path.cwd()

        return Assistant(
            settings=self.settings,
            offices=self.offices,
            handbook=self.handbook,
            rng=rng,
            base_dir=base_dir,
        )

    def test_greeting(self) -> None:
        assistant = (
            self.make_assistant()
        )

        response = assistant.handle(
            "hi"
        )

        self.assertEqual(
            response.status,
            Status.OK,
        )

        self.assertEqual(
            response.message,
            (
                "Hello! I can help with "
                "offices, fees and rules."
            ),
        )

    def test_empty_input(
        self,
    ) -> None:
        assistant = (
            self.make_assistant()
        )

        response = assistant.handle(
            ""
        )

        self.assertEqual(
            response.status,
            Status.EMPTY_INPUT,
        )

        self.assertEqual(
            response.message,
            "empty",
        )

    def test_fee(
        self,
    ) -> None:
        assistant = (
            self.make_assistant()
        )

        response = assistant.handle(
            (
                "tuition for "
                "18 credits "
                "and 2 retake"
            )
        )

        self.assertEqual(
            response.status,
            Status.OK,
        )

        self.assertEqual(
            response.message,
            (
                "Your tuition is "
                "9450000 VND"
            ),
        )

    def test_too_many_credits(
        self,
    ) -> None:
        assistant = (
            self.make_assistant()
        )

        response = assistant.handle(
            "tuition 40 credits"
        )

        self.assertEqual(
            response.status,
            Status.TOO_MANY_CREDITS,
        )

        self.assertEqual(
            response.message,
            "too many credits",
        )

    def test_office_lookup(
        self,
    ) -> None:
        assistant = (
            self.make_assistant()
        )

        response = assistant.handle(
            "where is the library"
        )

        self.assertEqual(
            response.status,
            Status.OK,
        )

        self.assertEqual(
            response.message,
            (
                "Library: room A101, "
                "open 08:00-17:00"
            ),
        )

    def test_rule_uses_llm(
        self,
    ) -> None:
        assistant = (
            self.make_assistant(
                rng=lambda: 0.5
            )
        )

        response = assistant.handle(
            "can I register my thesis"
        )

        self.assertEqual(
            response.status,
            Status.OK,
        )

        self.assertIn(
            "Here is what I found:",
            response.message,
        )

        self.assertIn(
            "(source: RULE-1)",
            response.message,
        )

    def test_llm_timeout_fallback(
        self,
    ) -> None:
        assistant = (
            self.make_assistant(
                rng=lambda: 0.05
            )
        )

        response = assistant.handle(
            "can I register my thesis"
        )

        self.assertEqual(
            response.status,
            Status.OK,
        )

        self.assertEqual(
            response.message,
            (
                "Students may register "
                "a thesis after "
                "120 credits. "
                "(source: RULE-1)"
            ),
        )

    def test_save_history(
        self,
    ) -> None:
        with (
            tempfile.TemporaryDirectory()
            as temp_dir
        ):
            assistant = (
                self.make_assistant(
                    base_dir=Path(
                        temp_dir
                    )
                )
            )

            assistant.handle(
                "hi"
            )

            response = (
                assistant.handle(
                    "save history.txt"
                )
            )

            self.assertEqual(
                response.status,
                Status.SAVED,
            )

            path = (
                Path(temp_dir)
                / "history.txt"
            )

            content = (
                path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                content,
                (
                    "hi\n"
                    "save history.txt\n"
                ),
            )


if __name__ == "__main__":
    unittest.main()