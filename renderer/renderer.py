from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
from typing import TypeAlias
import PIL.ImageOps
from PIL.Image import Image, open as open_image, new as new_image, Resampling
import base64
import numpy

TILE_SIZE = 32
atlas: Image = open_image(os.path.join(os.path.dirname(__file__), "sprites/atlas.png"))

Float2: TypeAlias = tuple[float, float]
Int2: TypeAlias = tuple[int, int]

@dataclass()
class Vector2:
    value: Float2

    def toint2(self) -> Int2:
        return (int(self.value[0]), int(self.value[1]))


class Sprite():
    center: Float2
    image: Image

    def __init__(
        self,
        atlas: Image,
        position: Int2,
        size: Int2,
        center: Float2
    ):
        self.center = center

        x1 = position[0] * TILE_SIZE
        y1 = position[1] * TILE_SIZE
        x2 = x1 + size[0] * TILE_SIZE
        y2 = y1 + size[1] * TILE_SIZE

        self.image = atlas.crop((x1, y1, x2, y2))


class GameObject(ABC):
    sptire: Sprite
    position: Vector2

    @abstractmethod
    def update(self): ...


class Beast(GameObject):
    def __init__(self, position: Float2):
        super().__init__()

        self.sptire = Sprite(atlas, (0, 0), (1, 1), (0.5, 1))
        self.position = Vector2(position)

    def update(self):
        pass


class Hunter(GameObject):
    def __init__(self, position: Float2):
        super().__init__()

        self.sptire = Sprite(atlas, (0, 1), (1, 1), (0.5, 1))
        self.position = Vector2(position)

    def update(self):
        pass


scene = [
    Beast((116, 0)),
    Beast((124, 0)),
    Beast((192, 0)),
    Hunter((64, 0))
]

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
    pass
    # global beast_speed, beast_dir, beast_accel
    # beast_dir = random.choice((-1, 1))
    # beast.position = (sw // 2 + beast_dir * random.randint(0, (sw // 4)),0)
    # shot.position = (0, 0)
    # # beast_speed = (random.random() * 1) + 1
    # beast_speed = 1
    # beast_accel = 0.7 + random.random()


class Renderer():
    _bg_color = (225, 218, 197, 255) # (255, 255, 255, 255) #

    def render(self, *, debug: bool = False) -> Image:
        frame = new_image(atlas.mode, (CAMERA_WIDTH, VIEW_HEIGHT), self._bg_color)


        for go in scene:
            world_pos = go.position.toint2()

            view_pos = (
                world_pos[0] - int(go.sptire.image.size[0] * go.sptire.center[0]),
                VIEW_HEIGHT - int(go.sptire.image.size[1] * go.sptire.center[1]) - world_pos[1],
            )
            frame.paste(go.sptire.image, view_pos, go.sptire.image)


        # white_frame = PIL.ImageOps.invert(frame)
        # big_frame = white_frame.resize(tuple(d*2 for d in white_frame.size), Resampling.NEAREST)
        big_frame = frame.resize((FRAME_WIDTH, FRAME_HEIGHT), Resampling.NEAREST)
        # l_frame = big_frame.convert("L") # иначе не сохранить в хранилище


        return big_frame
        # return [l_frame.crop((i*328, 0, (i+1)*328, 480)) for i in range(3)]

    def hash_image(self, img: Image) -> str:
        assert img.mode == "1", "Функция ожидает 1-bit изображение"

        resized = img.resize((32,32), Resampling.BILINEAR)
        return base64.b32encode(numpy.packbits(resized)).decode('utf-8')
