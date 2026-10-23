from typing import Dict
from typing import List
from typing import Optional

from models import Response
from models import Status


def find_office(
    message: str,
    offices: Dict[str, List[str]],
) -> Optional[Response]:
    for key, office in offices.items():
        if key in message:
            return Response(
                Status.OK,
                (
                    f"{office[0]}: "
                    f"room {office[1]}, "
                    f"open {office[2]}"
                ),
            )

    return None