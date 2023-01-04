from enum import Enum, auto
from typing import Optional

from pygame import Surface
from pygame.color import Color
from pygame.font import Font

from bfrl import constants
from bfrl import game_globals as gg
from bfrl import panels
from bfrl.structs import Vector


class TextAlignment(Enum):
    TOP_LEFT = auto()
    CENTER = auto()


def game() -> None:

    assert gg.SURFACE_MAIN
    assert gg.SURFACE_MAP
    assert gg.ASSETS
    assert gg.GAME
    assert gg.GAME.current_map

    gg.SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    gg.SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

    # draw map
    map_surface()

    # draw movment range
    movement_range()

    # draw objects in map
    objects()

    gg.SURFACE_MAIN.blit(gg.SURFACE_MAP, (0, 0))

    if gg.GAME.turn_order_panel:
        panels.turn_order()

    if gg.GAME.messages_panel and gg.GAME.message_count:
        panels.messages()


def map_surface():
    assert gg.GAME
    assert gg.SURFACE_MAP
    assert gg.ASSETS

    for pos, tile in gg.GAME.current_map.tiles.items():
        tile = gg.ASSETS.tile(tile.type, tile.explored, tile.facing)
        offset = pos.elementwise() * constants.CELL_SIZE
        gg.SURFACE_MAP.blit(tile, offset)


def objects():
    assert gg.GAME
    for obj in gg.GAME.current_map.object_list:
        obj.draw()


def movement_range():
    assert gg.GAME
    max_distance = gg.GAME.time_left + 1
    for tile in gg.GAME.active_actor.origin.in_range(max_distance):
        if gg.GAME.current_map.check_for_wall(tile):
            continue
        paint_tile(tile)


def text(
    text: str,
    surface: Surface,
    font: Font,
    coord: Vector,
    color: Color,
    bg_color: Optional[Color] = None,
    alignment: TextAlignment = TextAlignment.TOP_LEFT,
) -> None:

    text_surface = font.render(text, False, color, bg_color)
    text_rect = text_surface.get_rect()
    if alignment == TextAlignment.CENTER:
        text_rect.center = (int(coord.x), int(coord.y))
    else:
        text_rect.topleft = (int(coord.x), int(coord.y))

    surface.blit(text_surface, text_rect)


def paint_tile(coord: Vector, color: Color = constants.COLOR_WHITE, alpha: int = 150):

    assert gg.SURFACE_MAP

    target = coord.elementwise() * constants.CELL_SIZE
    tile = Surface(constants.CELL_SIZE)
    tile.fill(color)
    tile.set_alpha(alpha)

    gg.SURFACE_MAP.blit(tile, target)
