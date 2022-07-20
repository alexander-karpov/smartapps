from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
from typing import TypeAlias
import PIL.ImageOps
from PIL.Image import Image, open as open_image, new as new_image, Resampling
import base64
import numpy as np

TILE_SIZE = 32
STEP_SIZE = TILE_SIZE // 2


with open_image(os.path.join(os.path.dirname(__file__), "sprites/atlas.png")) as atlas:
    atlas.load()


Float2: TypeAlias = tuple[float, float]
Int2: TypeAlias = tuple[int, int]


class Sprite:
    center: Float2
    image: Image
    mirrored: Image

    def __init__(self, atlas: Image, position: Int2, size: Int2, center: Float2):
        self.center = center

        x1 = position[0] * TILE_SIZE
        y1 = position[1] * TILE_SIZE
        x2 = x1 + size[0] * TILE_SIZE
        y2 = y1 + size[1] * TILE_SIZE

        self.image = atlas.crop((x1, y1, x2, y2))
        self.mirrored = PIL.ImageOps.mirror(self.image)


class GameObject(ABC):
    sptire: Sprite
    position: np.ndarray

    @abstractmethod
    def update(self):
        ...

    @property
    def image(self) -> Image:
        return self.sptire.image


class Beast(GameObject):
    velocity: np.ndarray
    looks_forward: bool

    def __init__(self, position: Float2):
        super().__init__()

        self.sptire = Sprite(atlas, (0, 0), (1, 1), (0.5, 1))
        self.position = np.array(position, dtype=float)
        self.velocity = np.array((-0.5, 0.0), dtype=float)

    def update(self):
        self.position += self.velocity * STEP_SIZE
        self.looks_forward = self.velocity[0] >= 0

    @property
    def image(self) -> Image:
        if self.looks_forward:
            return self.sptire.image

        return self.sptire.mirrored


class Hunter(GameObject):
    def __init__(self, position: Float2):
        super().__init__()

        self.sptire = Sprite(atlas, (0, 1), (1, 1), (0.5, 1))
        self.position = np.array(position)

    def update(self):
        pass


scene = [Beast((116, 0)), Beast((124, 0)), Beast((192, 0)), Hunter((64, 0))]


FRAME_WIDTH = 776
CAMERA_WIDTH = FRAME_WIDTH // 3
FRAME_HEIGHT = 344
VIEW_HEIGHT = FRAME_HEIGHT // 3
steps_n = 12


# beast_speed = (random.random() * 1) + 1
# beast_dir = 1
# beast_accel = 1
# hunter = GameObject(PIL.ImageOps.invert(open_image(os.path.join(os.path.dirname(__file__), "sprites/hunter_x.png")).convert("1")), (0, 0))
# shot = GameObject(new_image("L", (sw // steps_n, 1), (255)).convert("1"), (0, 0))


def shoot(d) -> None:
    pass
    # global beast_speed, beast_accel
    # one_d = sw // steps_n
    # hunter_bow_x = hunter.position[0] + 26

    # beast.position = (beast.position[0] - one_d * int(beast_speed * beast_dir),0)
    # beast_speed = beast_speed + beast_accel

    # shot.position = (hunter.position[0] + hunter_bow_x  + one_d * (d - 1), 12)


def update():
    for go in scene:
        go.update()
    # global beast_speed, beast_dir, beast_accel
    # beast_dir = random.choice((-1, 1))
    # beast.position = (sw // 2 + beast_dir * random.randint(0, (sw // 4)),0)
    # shot.position = (0, 0)
    # # beast_speed = (random.random() * 1) + 1
    # beast_speed = 1
    # beast_accel = 0.7 + random.random()


class Renderer:
    _bg_color = (225, 218, 197, 255)  # (255, 255, 255, 255) #

    def render(self, *, debug: bool = False) -> Image:
        frame = new_image(atlas.mode, (CAMERA_WIDTH, VIEW_HEIGHT), self._bg_color)

        for go in scene:
            view_pos = (
                int(go.position[0] - go.sptire.image.size[0] * go.sptire.center[0]),
                int(
                    VIEW_HEIGHT
                    - go.sptire.image.size[1] * go.sptire.center[1]
                    - go.position[1]
                ),
            )

            frame.paste(go.image, view_pos, go.image)

        # white_frame = PIL.ImageOps.invert(frame)
        # big_frame = white_frame.resize(tuple(d*2 for d in white_frame.size), Resampling.NEAREST)
        big_frame = frame.resize((FRAME_WIDTH, FRAME_HEIGHT), Resampling.NEAREST)
        # l_frame = big_frame.convert("L") # иначе не сохранить в хранилище

        return big_frame
        # return [l_frame.crop((i*328, 0, (i+1)*328, 480)) for i in range(3)]

    def hash_image(self, img: Image) -> str:
        assert img.mode == "1", "Функция ожидает 1-bit изображение"

        resized = img.resize((32, 32), Resampling.BILINEAR)
        return base64.b32encode(numpy.packbits(resized)).decode("utf-8")
