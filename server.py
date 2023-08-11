import asyncio
import json
from typing import Literal
from db import db
from mogno_logger import MognoLogger

logger = MognoLogger(db, "hagi2")


async def app(scope, receive, send):
    assert scope["type"] == "http"
    assert scope["method"] == "POST"

    request = json.loads(await read_body(receive))

    match detect_app(request):
        case "hagi":
            from hagi import get_dialog

            dialog = get_dialog(request["session"]["session_id"])
        case "stories":
            from stories import get_dialog

            dialog = get_dialog(request["session"]["session_id"])

    assert dialog, "Хоть один диалог выбран"

    response = await dialog.handle_request(request)

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(response, ensure_ascii=False).encode("utf-8"),
        }
    )

    # Для того, чтобы after_response наверняка выполнялся после отправки ответа
    await asyncio.sleep(0.001)

    dialog.after_response()
    logger.log(request, response)


async def read_body(receive):
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    return body


def detect_app(request) -> Literal["stories"] | Literal["hagi"]:
    if request["session"]["skill_id"] == "2f2e926e-66c8-4f66-b628-18255c83e588":
        return "stories"

    return "hagi"
