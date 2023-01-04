from typing import Optional

from pygame import Surface
from pygame.time import Clock

from bfrl.assets import Assets
from bfrl.game import GameObject

SURFACE_MAIN: Optional[Surface]
SURFACE_MAP: Optional[Surface]
ASSETS: Optional[Assets]
GAME: Optional[GameObject]
CLOCK: Optional[Clock]


def init() -> None:

    global SURFACE_MAIN, SURFACE_MAP
    global ASSETS, GAME
    global CLOCK

    SURFACE_MAIN = None
    SURFACE_MAP = None
    ASSETS = None
    GAME = None
    CLOCK = None
