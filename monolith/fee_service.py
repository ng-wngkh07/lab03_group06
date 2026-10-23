from models import Response, Status


def handle_fee(
    message: str,
    rate: int,
    retake_rate: float,
) -> Response:
    words = (
        message
        .replace("?", " ")
        .split()
    )

    credits = 0
    retake = 0

    for index, word in enumerate(words):
        if not word.isdigit():
            continue

        value = int(word)

        if (
            index + 1 < len(words)
            and words[index + 1].startswith(
                "retake"
            )
        ):
            retake = value

        elif credits == 0:
            credits = value

    if credits == 0:
        return Response(
            Status.MISSING_CREDITS,
            "How many credits?",
        )

    if credits > 30:
        return Response(
            Status.TOO_MANY_CREDITS,
            "too many credits",
        )

    total = (
        credits * rate
        + retake
        * rate
        * retake_rate
    )

    return Response(
        Status.OK,
        f"Your tuition is {int(total)} VND",
    )