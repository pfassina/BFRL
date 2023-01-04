from dataclasses import dataclass
from enum import Enum, auto
from itertools import product

from bfrl import maps
from bfrl.actors import Actor
from bfrl.generator import CreatureType
from bfrl.structs import TileType, Vector


class PlayerAction(Enum):
    NONE = auto()
    QUIT = auto()
    MOVED = auto()
    ATTACKED = auto()
    END_TURN = auto()


class GameState(Enum):
    PLAYER = auto()
    QUIT = auto()


@dataclass
class GameObject:
    current_map: maps.GameMap
    state: GameState

    def __post_init__(self) -> None:
        self.turn_order_panel: bool = True
        self.messages_panel: bool = True
        self._message_history: list[str] = []

    @property
    def turn_order(self) -> list[Actor]:
        return sorted([a for a in self.current_map.creature_list])

    @property
    def active_actor(self) -> Actor:
        return self.turn_order[0]

    @property
    def time_left(self) -> int:
        return self.turn_order[1].initiative if len(self.turn_order) > 1 else -1

    @property
    def last_message(self) -> str:
        return self._message_history[-1]

    @property
    def message_count(self) -> int:
        return len(self._message_history)

    def message(self, message: str) -> None:
        self._message_history.append(message)

    def reset_turn(self) -> None:

        self.active_actor.end_movement()

        delta = self.active_actor.initiative
        for a in self.turn_order:
            a.delay(-1 * delta)

    def toggle_panel(self, panel) -> None:
        if panel == "turn_order":
            self.turn_order_panel = not self.turn_order_panel
            return
        if panel == "messages":
            self.messages_panel = not self.messages_panel
            return


@dataclass
class Scenario:
    _raw_tiles: list[list[int]]
    _raw_actors: dict[str, tuple[int, int]]

    @property
    def _width(self) -> int:
        return len(self._raw_tiles[0])

    @property
    def _height(self) -> int:
        return len(self._raw_tiles)

    @property
    def size(self) -> Vector:
        return Vector(self._width, self._height)

    @property
    def tiles(self) -> dict[Vector, TileType]:
        tile_dict = {
            0: TileType["FLOOR"],
            1: TileType["WALL"],
        }
        return {
            Vector(x, y): tile_dict[self._raw_tiles[y][x]]
            for x, y in product(range(self._width), range(self._height))
        }

    @property
    def actors(self) -> list[tuple[CreatureType, Vector]]:
        return [(CreatureType[c], Vector(*v)) for c, v in self._raw_actors]
