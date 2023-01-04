from __future__ import annotations

from enum import Enum, auto

import pygame


class Vector(pygame.Vector2):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    @property
    def neighbors(self) -> dict[str, Vector]:
        return {
            "w": Vector(self.x - 1, self.y),
            "e": Vector(self.x + 1, self.y),
            "n": Vector(self.x, self.y - 1),
            "s": Vector(self.x, self.y + 1),
            "nw": Vector(self.x - 1, self.y - 1),
            "sw": Vector(self.x - 1, self.y + 1),
            "ne": Vector(self.x + 1, self.y - 1),
            "se": Vector(self.x + 1, self.y + 1),
        }

    def distance(self, other: Vector) -> float:
        return abs(other.x - self.x) + abs(other.y - self.y)

    def in_range(self, radius: int) -> list[Vector]:
        return [
            Vector(x + self.x, y + self.y)
            for x in range(-radius, radius + 1)
            for y in range(-radius, radius + 1)
            if abs(x) + abs(y) <= radius
        ]


class Direction(Enum):
    NORTH = Vector(0, -1)
    SOUTH = Vector(0, +1)
    WEST = Vector(-1, 0)
    EAST = Vector(+1, 0)


class TileType(Enum):
    FLOOR = auto()
    WALL = auto()
    TARGET = auto()


class SpriteType(Enum):
    # characters
    A_PLAYER = auto()
    A_SNAKE_01 = auto()
    A_SNAKE_02 = auto()
    A_MOUSE_01 = auto()

    # items
    S_SWORD = auto()
    S_SHIELD = auto()
    S_SCROLL_01 = auto()
    S_SCROLL_02 = auto()
    S_SCROLL_03 = auto()
    S_FLESH_01 = auto()
    S_FLESH_02 = auto()

    # Special
    S_STAIRS_UP = auto()
    S_STAIRS_DOWN = auto()
    S_MAGIC_LAMP = auto()
    S_PORTAL_OPEN = auto()
    S_PORTAL_CLOSED = auto()
