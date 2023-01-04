from typing import Optional

import pygame

from bfrl import draw
from bfrl import game_globals as gg
from bfrl.constants import GAME_FPS, MAP_HEIGHT, MAP_WIDTH
from bfrl.cursor import Cursor
from bfrl.structs import Direction, Vector


def tile_select(
    origin: Vector,
    max_range: int = MAP_HEIGHT + MAP_WIDTH,
    ignore_walls: bool = True,
    ignore_creatures: bool = True,
    radius: int = 0,
) -> list[Vector]:

    assert gg.SURFACE_MAIN
    assert gg.SURFACE_MAP
    assert gg.CLOCK

    cursor = Cursor(origin, max_range, ignore_walls, ignore_creatures, radius)

    while True:

        events = _get_player_input()

        if _quit_menu(events):
            return []

        direction = _get_direction(events)

        cursor.move(direction)

        draw.map_surface()

        for tile in cursor.valid_selection:
            draw.paint_tile(tile)

        draw.objects()
        cursor.draw()

        gg.SURFACE_MAIN.blit(gg.SURFACE_MAP, (0, 0))
        gg.CLOCK.tick(GAME_FPS)
        pygame.display.flip()

        if _confirm_selection(events):
            return cursor.target


def _get_player_input() -> list[int]:
    return [e.key for e in pygame.event.get() if e.type == pygame.KEYDOWN]


def _get_direction(events: list[int]) -> Optional[Direction]:
    if pygame.K_UP in events:
        return Direction.NORTH
    if pygame.K_RIGHT in events:
        return Direction.EAST
    if pygame.K_DOWN in events:
        return Direction.SOUTH
    if pygame.K_LEFT in events:
        return Direction.WEST


def _quit_menu(events: list[int]) -> bool:
    return pygame.K_ESCAPE in events


def _confirm_selection(events: list[int]) -> bool:
    return pygame.K_SPACE in events
