import io
import os
import json
from typing import Tuple
from PIL import Image
import requests

SPRITE_SIDE = 64

sprites = []

# Load sprites
with Image.open("./sprites/roguelike.png") as im:
    SPRITES_IN_LINE = im.size[0] // SPRITE_SIDE

    for i in range(56):
        x1 = SPRITE_SIDE * i % im.size[0]
        y1 = (i // SPRITES_IN_LINE) * SPRITE_SIDE

        part = im.crop((x1, y1, x1 + SPRITE_SIDE, y1 + SPRITE_SIDE))
        sprites.append(part)


def draw_sprite(frame: Image.Image, sprite: Image.Image, position: Tuple[int, int], mask=None):
    frame.paste(sprite, (position[0] * SPRITE_SIDE, position[1] * SPRITE_SIDE), mask)


def draw_scene(scene) -> Image.Image:
    SPRITES_IN_LINE = 6
    frame = Image.new("RGBA", (328, 480), (0,0,0,255))

    for (i, sprite_num) in enumerate(scene["background"]):
        draw_sprite(frame, sprites[sprite_num], (i % SPRITES_IN_LINE, i // SPRITES_IN_LINE))

    for sprite_id, x, y in scene["objects"]:
        draw_sprite(frame, sprites[sprite_id], (x, y), sprites[sprite_id])

    return frame


def handler(event, context):
    scene = json.loads(event['body'])

    frame = draw_scene(scene)
    output = io.BytesIO()
    frame.save(output, format='PNG')
    frame.close()

    resp = requests.api.post(
        f"https://dialogs.yandex.net/api/v1/skills/01aa8cf1-03ef-4549-8d0f-0389d85f7587/images",
        headers={
            "Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}",
        },
        files={'file': output.getvalue()}
    )

    output.close()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'isBase64Encoded': False,
        'body': resp.json()["image"]
    }
