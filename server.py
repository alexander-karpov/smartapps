import json
from smartapps.dialog.dialog_flow import get_dialog


async def app(scope, receive, send):
    assert scope['type'] == 'http'
    assert scope['method'] == 'POST'

    request = json.loads(await read_body(receive))
    dialog = get_dialog(request)
    response = dialog.handle_request(request)

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
