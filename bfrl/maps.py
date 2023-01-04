from dataclasses import dataclass
from itertools import product
from typing import Optional

from bfrl.actors import Actor
from bfrl.structs import TileType, Vector


@dataclass
class Tile:
    type: TileType
    explored: bool = True
    facing: int = 0


@dataclass
class GameMap:
    size: Vector
    raw_tiles: dict[Vector, TileType]

    def __post_init__(self) -> None:

        self.object_list: list[Actor] = []

        self.width = self.size.x
        self.height = self.size.y
        self.tiles: dict[Vector, Tile] = self.generate_tiles()
        self.determine_facing()

    def generate_tiles(self) -> dict[Vector, Tile]:
        return {Vector(x, y): Tile(t) for (x, y), t in self.raw_tiles.items()}

    def determine_facing(self) -> None:

        for pos, tile in self.tiles.items():

            if tile.type != TileType.WALL:
                continue

            neighbors = pos.neighbors.values()
            if all([self.check_for_wall(n) for n in neighbors]):
                self.tiles[pos].facing = 998
                continue

        for pos, tile in self.tiles.items():

            if tile.type != TileType.WALL:
                continue
            if tile.facing != 0:
                continue

            n = self.tiles.get(pos.neighbors["n"])
            e = self.tiles.get(pos.neighbors["e"])
            s = self.tiles.get(pos.neighbors["s"])
            w = self.tiles.get(pos.neighbors["w"])

            facing = 0
            if n:
                is_wall = n.type == TileType.WALL
                is_edge = n.facing <= 99
                facing += 1 if is_wall & is_edge else 0
            if e:
                is_wall = e.type == TileType.WALL
                is_edge = e.facing <= 99
                facing += 2 if is_wall & is_edge else 0
            if s:
                is_wall = s.type == TileType.WALL
                is_edge = s.facing <= 99
                facing += 4 if is_wall & is_edge else 0
            if w:
                is_wall = w.type == TileType.WALL
                is_edge = w.facing <= 99
                facing += 8 if is_wall & is_edge else 0

            self.tiles[pos].facing = facing

    def add_object(self, object: Actor) -> None:
        self.object_list.append(object)

    def remove_object(self, object: Actor) -> None:
        self.object_list.remove(object)

    def check_for_wall(self, target: Vector) -> bool:
        tile = self.tiles.get(target)
        if tile:
            return tile.type == TileType.WALL
        return True

    def check_for_object(self, target: Vector) -> Optional[Actor]:
        for obj in self.object_list:
            if obj.coord == target:
                return obj
        return None

    @property
    def creature_list(self) -> list[Actor]:
        return [c for c in self.object_list if c.creature]

    def in_bounds(self, target: Vector) -> bool:
        return Vector(0, 0) <= target.elementwise() < self.size
