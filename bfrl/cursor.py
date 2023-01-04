from dataclasses import dataclass
from typing import Optional

from bfrl import game_globals as gg
from bfrl.constants import CELL_SIZE, MAP_HEIGHT, MAP_WIDTH
from bfrl.maps import Tile
from bfrl.structs import Direction, TileType, Vector


@dataclass
class Cursor:

    origin: Vector
    max_range: int = MAP_HEIGHT + MAP_WIDTH
    ignore_walls: bool = True
    ignore_creatures: bool = True
    radius: int = 0

    def __post_init__(self) -> None:
        self._coord: Vector = self.origin.copy()

    @property
    def valid_selection(self) -> list[Vector]:
        assert gg.GAME
        return [
            coord
            for coord in self.origin.in_range(self.max_range)
            if gg.GAME.current_map.in_bounds(coord)
        ]

    @property
    def target(self) -> list[Vector]:
        assert gg.GAME
        return [
            target
            for target in self._coord.in_range(self.radius)
            if gg.GAME.current_map.in_bounds(target)
        ]

    @property
    def _tiles(self) -> list[Tile]:
        tiles = [Tile(TileType.TARGET) for _ in self.target]

        for coord, tile in zip(self.target, tiles):
            neighbors = coord.neighbors.values()
            if all([n in self.target for n in neighbors]):
                tile.facing = 998

        for coord, tile in zip(self.target, tiles):

            if tile.facing != 0:
                continue

            n = (
                self.target.index(coord.neighbors["n"])
                if coord.neighbors["n"] in self.target
                else None
            )
            e = (
                self.target.index(coord.neighbors["e"])
                if coord.neighbors["e"] in self.target
                else None
            )
            s = (
                self.target.index(coord.neighbors["s"])
                if coord.neighbors["s"] in self.target
                else None
            )
            w = (
                self.target.index(coord.neighbors["w"])
                if coord.neighbors["w"] in self.target
                else None
            )

            if n is not None:
                tile.facing += 1
            if e is not None:
                tile.facing += 2
            if s is not None:
                tile.facing += 4
            if w is not None:
                tile.facing += 8

        return tiles

    def move(self, direction: Optional[Direction]) -> None:

        assert gg.GAME

        if not direction:
            return

        game_map = gg.GAME.current_map
        new_coord = self._coord + direction.value

        if not game_map.in_bounds(new_coord):
            return

        if (not self.ignore_walls) and game_map.check_for_wall(new_coord):
            return

        if (not self.ignore_creatures) and game_map.check_for_object(new_coord):
            return

        if self.origin.distance(new_coord) > self.max_range:
            return

        self._coord = new_coord

    def draw(self) -> None:
        assert gg.GAME
        assert gg.SURFACE_MAP
        assert gg.ASSETS

        if (not self.target) or (not self._tiles):
            return

        for pos, tile in zip(self.target, self._tiles):
            tile = gg.ASSETS.tile(tile.type, tile.explored, tile.facing)
            offset = pos.elementwise() * CELL_SIZE
            gg.SURFACE_MAP.blit(tile, offset)
