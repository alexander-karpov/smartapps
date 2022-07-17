import sys
import os
from typing import TypeAlias
import PIL.ImageOps
from PIL.Image import Image, open as open_image, new as new_image, Resampling
import random
import base64
import numpy

Vector2: TypeAlias = tuple[int, int]
Vector2Float: TypeAlias = tuple[float, float]

def hash_image(img: Image) -> str:
	assert img.mode == "1", "Функция ожидает 1-bit изображение"

	resized = img.resize((32,32), Resampling.BILINEAR)
	return base64.b32encode(numpy.packbits(resized)).decode('utf-8')

class GameObject():
    sptire: Image
    position: Vector2

    def __init__(self, sptire, position: Vector2) -> None:
        self.sptire = sptire
        self.position = position

# class Beast(GameObject):
#     _velocity: float
#     _direction: Literal[1] | Literal[-1]
#     _acceleration: float

#     def __init__(self, sptire, position: Vector2) -> None:
#         super().__init__(sptire, position)

#         self._velocity = 0
#         self._direction = 1
#         self._acceleration = 0


#     def position() -> Vector2:


beast = GameObject(PIL.ImageOps.invert(open_image(os.path.join(os.path.dirname(__file__), "sprites/beast.png")).convert("1")), (200, 0))
beast_speed = (random.random() * 1) + 1
beast_dir = 1
beast_accel = 1
hunter = GameObject(PIL.ImageOps.invert(open_image(os.path.join(os.path.dirname(__file__), "sprites/hunter_x.png")).convert("1")), (0, 0))
shot = GameObject(new_image("1", ((328 // 2) // 5, 1), (1)), (0, 0))


def shoot(d) -> None:
    global beast_speed, beast_accel
    one_d = (328 // 2) // 5
    hunter_bow_x = hunter.position[0] + 26

    beast.position = (beast.position[0] - one_d * int(beast_speed * beast_dir),0)
    beast_speed = beast_speed + beast_accel

    shot.position = (hunter.position[0] + hunter_bow_x  + one_d * (d - 1), 16)

def update():
    global beast_speed, beast_dir, beast_accel
    beast_dir = random.choice((-1, 1))
    beast.position = (int((328 // 2) * 1.5) + beast_dir * random.randint(0, (328 // 2)),0)
    shot.position = (0, 0)
    # beast_speed = (random.random() * 1) + 1
    beast_speed = 1
    beast_accel = 0.7 + random.random()


class Renderer():
    _bg_color = (225, 218, 197, 255)
    _screen_size = ((328 // 2) * 3, 480 // 2)

    def render(self, *, debug: bool = False) -> list[Image]:
        frame = new_image("1", self._screen_size, (0))

        if debug:
            border = new_image("1", (1, self._screen_size[1]), (1))

            for x in range(2):
                frame.paste(border, ((x + 1) * (328 // 2), 0), border)

        for o in [beast, hunter, shot]:
            # pos = (
            #     random.randint(10, frame.size[0] - obj.sptire.size[0] - 10),
            #     random.randint(10, frame.size[1] - obj.sptire.size[1] - 10),
            # )

            pos = (
                o.position[0],
                -o.position[1] + self._screen_size[1] - o.sptire.size[1],
            )

            frame.paste(o.sptire, pos)


        white_frame = PIL.ImageOps.invert(frame)
        big_frame = white_frame.resize(tuple(d*2 for d in white_frame.size), Resampling.NEAREST)
        l_frame = big_frame.convert("L") # иначе не сохранить в хранилище

        if debug:
            return l_frame  # type: ignore

        return [l_frame.crop((i*328, 0, (i+1)*328, 480)) for i in range(3)]



sprites = []

# c = open_image("./sprites/cb.png")
# mc = open_image("./sprites/mcb.png")

# # Load sprites
# with Image.open("./sprites/roguelike.png") as im:
#     SPRITES_IN_LINE = im.size[0] // SPRITE_SIDE

#     for i in range(56):
#         x1 = SPRITE_SIDE * i % im.size[0]
#         y1 = (i // SPRITES_IN_LINE) * SPRITE_SIDE

#         part = im.crop((x1, y1, x1 + SPRITE_SIDE, y1 + SPRITE_SIDE))
#         sprites.append(part)


# def draw_sprite(frame: Image.Image, sprite: Image.Image, position: Tuple[int, int], mask=None):



# def draw_scene(scene) -> Image.Image:
#     SPRITES_IN_LINE = 6

#     frame = Image.new("RGBA", GALLERY_IMAGE_SIZE, (225, 218, 197,255))

#     # for (i, sprite_num) in enumerate(scene["background"]):
#     #     draw_sprite(frame, sprites[sprite_num], (i % SPRITES_IN_LINE, i // SPRITES_IN_LINE))

#     for sprite_id, x, y in scene["objects"]:
#         draw_sprite(frame, sprites[sprite_id], (x, y), sprites[sprite_id])

#         draw_sprite(frame, c, (2, 1), c)
#         draw_sprite(frame, mc, (3, 4), mc)

#     return frame

# def upload(scene):
#     frame = draw_scene(scene)
#     output = io.BytesIO()
#     frame.save(output, format='PNG')
#     frame.close()

#     resp = requests.api.post(
#         f"https://dialogs.yandex.net/api/v1/skills/01aa8cf1-03ef-4549-8d0f-0389d85f7587/images",
#         headers={
#             "Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}",
#         },
#         files={'file': output.getvalue()}
#     )

#     output.close()

#     return resp.json()["image"]
