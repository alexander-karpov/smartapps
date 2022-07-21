from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
from typing import TypeAlias
import PIL.ImageOps
from PIL.Image import Image, open as open_image, new as new_image, Resampling
import base64
import numpy as np
import itertools

TILE_SIZE = 32
STEP_SIZE = TILE_SIZE // 2


with open_image(os.path.join(os.path.dirname(__file__), "sprites/atlas.png")) as atlas:
    atlas.load()


Float2: TypeAlias = tuple[float, float]
Int2: TypeAlias = tuple[int, int]


@dataclass
class Sprite:
    image: Image
    mirrored: Image | None
    center: Float2

    @staticmethod
    def from_atlas(
        atlas: Image, position: Int2, size: Int2, center: Float2
    ) -> "Sprite":
        left_top = np.array(position) * TILE_SIZE
        right_bottom = np.array(size) * TILE_SIZE + left_top

        image = atlas.crop((*left_top, *right_bottom))

        return Sprite(image, PIL.ImageOps.mirror(image), center)

    @staticmethod
    def from_image(image: Image, center: Float2) -> "Sprite":
        return Sprite(image, None, center)


class GameObject(ABC):
    sptire: Sprite
    position: np.ndarray
    destroyed: bool

    def __init__(self, sptire: Sprite, position: Float2) -> None:
        super().__init__()

        self.sptire = sptire
        self.position = np.array(position, dtype=float)
        self.destroyed = False

    @abstractmethod
    def update(self):
        ...

    @property
    def image(self) -> Image:
        return self.sptire.image

    def destroy(self):
        self.destroyed = True


class RigidBody(GameObject):
    _bounds: np.ndarray

    def __init__(self, sptire: Sprite, position: Float2, bounds: Float2) -> None:
        assert bounds[0] <= bounds[1]

        super().__init__(sptire, position)

        self._bounds = np.array(bounds, dtype=float)

    def world_bounds(self) -> np.ndarray:
        return (
            self._bounds * TILE_SIZE
            + self.position[0]
            - self.image.size[0] * self.sptire.center[0]
        )

    def collision(self, go: "RigidBody") -> None:
        pass

    def detect_collision(self, go: "RigidBody") -> bool:
        a, b = go.world_bounds()
        my_bounds = self.world_bounds()

        a, b = go.world_bounds()

        return not (np.all(my_bounds < a) or np.all(my_bounds > b))


class Beast(RigidBody):
    velocity: np.ndarray
    looks_forward: bool

    def __init__(self, position: Float2):
        super().__init__(
            sptire=Sprite.from_atlas(atlas, (0, 0), (1, 1), (0.5, 1)),
            position=position,
            bounds=(0.25, 0.75),
        )

        self.velocity = np.array((-0.5, 0.0), dtype=float)

    def update(self):
        self.position += self.velocity * STEP_SIZE
        self.looks_forward = self.velocity[0] >= 0

    @property
    def image(self) -> Image:
        if self.looks_forward:
            return self.sptire.image

        return self.sptire.mirrored or self.sptire.image

    def hit(self):
        self.position[1] += 32

        self.destroy()


class Hunter(GameObject):
    def __init__(self, position: Float2):
        super().__init__(Sprite.from_atlas(atlas, (0, 1), (1, 1), (0.5, 1)), position)

    def update(self):
        pass


class Arrow(RigidBody):
    def __init__(self, position: Float2):
        super().__init__(
            Sprite.from_image(
                new_image("RGBA", (STEP_SIZE, 1), (0, 0, 0, 255)), (0, 0.25)
            ),
            position,
            bounds=(0, 0.5),
        )

    def update(self):
        self.destroy()

    def collision(self, go: "RigidBody"):
        super().collision(go)

        if isinstance(go, Beast):
            go.hit()


scene: list[GameObject] = [
    Beast((116, 0)),
    Beast((124, 0)),
    Beast((192, 0)),
    Hunter((64, 0)),
]


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
    global scene

    scene.append(Arrow((32 + STEP_SIZE * (d - 1), 12)))

    # global beast_speed, beast_accel
    # one_d = sw // steps_n
    # hunter_bow_x = hunter.position[0] + 26

    # beast.position = (beast.position[0] - one_d * int(beast_speed * beast_dir),0)
    # beast_speed = beast_speed + beast_accel

    # shot.position = (hunter.position[0] + hunter_bow_x  + one_d * (d - 1), 12)


def update():
    global scene

    for go in scene:
        go.update()

    for a, b in itertools.combinations(
        (go for go in scene if isinstance(go, RigidBody)), 2
    ):
        if a.detect_collision(b):
            a.collision(b)
            b.collision(a)

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


def drop_destroyed():
    global scene
    scene = [go for go in scene if not go.destroyed]
