import json
from typing import Literal
from db import db
from mogno_logger import MognoLogger

logger = MognoLogger(db, "hagi2")


async def app(scope, receive, send):
    assert scope['type'] == 'http'
    assert scope['method'] == 'POST'

    request = json.loads(await read_body(receive))

    match detect_app(request):
        case "hagi":
            from hagi import get_dialog
            dialog = get_dialog(request["session"]["session_id"])
        case "hunter":
            from hunter import get_dialog
            dialog = get_dialog(request["session"]["session_id"])

    assert dialog, 'Хоть один диалог выбран'

    response = await dialog.handle_request(request)

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'application/json'],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(response, ensure_ascii=False).encode('utf-8'),
    })

    dialog.after_response()
    logger.log(request, response)


async def read_body(receive):
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body


def detect_app(request) ->  Literal["hunter"] | Literal["hagi"]:
    if request["session"]["skill_id"] == '69eedbaf-4ac3-4df9-9381-fd9b3a66b67c':
        return 'hunter'

    return 'hagi'
