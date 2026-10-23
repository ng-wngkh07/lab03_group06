from typing import Any
from typing import Dict
from typing import List
from typing import Optional


def find_best_rule(
    message: str,
    handbook: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    best_rule = None
    best_score = 0

    for rule in handbook:
        text = str(
            rule.get(
                "text",
                "",
            )
        ).lower()

        score = 0

        for word in message.split():
            if (
                len(word) > 3
                and word in text
            ):
                score += 1

        if score > best_score:
            best_score = score
            best_rule = rule

    if best_score < 1:
        return None

    return best_rule