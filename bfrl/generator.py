from enum import Enum, auto

from bfrl import actors
from bfrl import game_globals as gg
from bfrl.structs import SpriteType, Vector


class CreatureType(Enum):
    PLAYER = auto()
    SNAKE_01 = auto()
    SNAKE_02 = auto()
    MOUSE_01 = auto()


def creatures(creature_list: list[tuple[CreatureType, Vector]]) -> None:
    for creature_type, coord in creature_list:
        creature(creature_type, coord)


def creature(creature: CreatureType, coord: Vector) -> None:
    creature_dict = {
        CreatureType.PLAYER: creature_player,
        CreatureType.SNAKE_01: creature_snake_01,
        CreatureType.SNAKE_02: creature_snake_02,
        CreatureType.MOUSE_01: creature_mouse,
    }
    creature_dict[creature](coord)


def creature_generator(creature: actors.Actor) -> None:
    assert gg.GAME
    gg.GAME.current_map.add_object(creature)


def creature_player(coord: Vector) -> None:
    actor = actors.Actor("Player", coord, SpriteType.A_PLAYER)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_snake_01(coord: Vector) -> None:
    actor = actors.Actor("Snake", coord, SpriteType.A_SNAKE_01)
    creature = actors.CreatureComponent(initiative=3)
    actor.add_component(creature)
    creature_generator(actor)


def creature_snake_02(coord: Vector) -> None:
    actor = actors.Actor("Python", coord, SpriteType.A_SNAKE_02)
    creature = actors.CreatureComponent(initiative=5)
    actor.add_component(creature)
    creature_generator(actor)


def creature_mouse(coord: Vector) -> None:
    actor = actors.Actor("Mouse", coord, SpriteType.A_MOUSE_01)
    creature = actors.CreatureComponent(initiative=2)
    actor.add_component(creature)
    creature_generator(actor)
