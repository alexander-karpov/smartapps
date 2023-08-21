"""
Сервер для Диалогов Алисы
"""
import asyncio
import json
from typing import Literal
from db import db
from mogno_logger import MognoLogger
from hagi import get_dialog as get_cat_dialog
from stories import get_dialog as get_stories_dialog

logger = MognoLogger(db)

DialogName = Literal["stories"] | Literal["cat"]


async def app(scope, receive, send):
    """
    Точка входа сервера Диалогов
    """
    assert scope["type"] == "http"
    assert scope["method"] == "POST"

    request = json.loads(await _read_body(receive))
    dialog_name = _dialog_name_by_id(request)

    match dialog_name:
        case "cat":
            dialog = get_cat_dialog(request["session"]["session_id"])
        case "stories":
            dialog = get_stories_dialog(request["session"]["session_id"])

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
    logger.log(request, response, dialog_name)


async def _read_body(receive):
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


def _dialog_name_by_id(request) -> DialogName:
    if request["session"]["skill_id"] == "2f2e926e-66c8-4f66-b628-18255c83e588":
        return "stories"

    return "stories"
