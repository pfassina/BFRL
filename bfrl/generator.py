from enum import Enum, auto

from bfrl import actors
from bfrl import game_globals as gg
from bfrl.structs import SpriteType, Vector


class CreatureType(Enum):
    WARRIOR = auto()
    ROGUE = auto()
    RANGER = auto()
    MAGE = auto()
    CLERIC = auto()
    DRUID = auto()
    BARBARIAN = auto()
    SWORDSMAN = auto()
    PALADIN = auto()
    GOBLIN = auto()
    GOBLIN_ARCHER = auto()
    GOBLIN_WARRIOR = auto()
    GOBLIN_NOBLE = auto()
    GOBLIN_MAGE = auto()


def creatures(creature_list: list[tuple[CreatureType, Vector]]) -> None:
    for creature_type, coord in creature_list:
        creature(creature_type, coord)


def creature(creature: CreatureType, coord: Vector) -> None:
    creature_dict = {
        CreatureType.WARRIOR: creature_warrior,
        CreatureType.ROGUE: creature_rogue,
        CreatureType.RANGER: creature_ranger,
        CreatureType.MAGE: creature_mage,
        CreatureType.CLERIC: creature_cleric,
        CreatureType.DRUID: creature_druid,
        CreatureType.BARBARIAN: creature_barbarian,
        CreatureType.SWORDSMAN: creature_swordsman,
        CreatureType.PALADIN: creature_paladin,
        CreatureType.GOBLIN: creature_goblin,
        CreatureType.GOBLIN_ARCHER: creature_goblin_archer,
        CreatureType.GOBLIN_WARRIOR: creature_goblin_warrior,
        CreatureType.GOBLIN_NOBLE: creature_goblin_noble,
        CreatureType.GOBLIN_MAGE: creature_goblin_mage,
    }
    creature_dict[creature](coord)


def creature_generator(creature: actors.Actor) -> None:
    assert gg.GAME
    gg.GAME.current_map.add_object(creature)


def creature_warrior(coord: Vector) -> None:
    actor = actors.Actor("Warrior", coord, SpriteType.A_WARRIOR)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_rogue(coord: Vector) -> None:
    actor = actors.Actor("Rogue", coord, SpriteType.A_ROGUE)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_ranger(coord: Vector) -> None:
    actor = actors.Actor("Ranger", coord, SpriteType.A_RANGER)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_mage(coord: Vector) -> None:
    actor = actors.Actor("Mage", coord, SpriteType.A_MAGE)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_cleric(coord: Vector) -> None:
    actor = actors.Actor("Cleric", coord, SpriteType.A_CLERIC)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_druid(coord: Vector) -> None:
    actor = actors.Actor("Druid", coord, SpriteType.A_DRUID)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_barbarian(coord: Vector) -> None:
    actor = actors.Actor("Barbarian", coord, SpriteType.A_BARBARIAN)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_swordsman(coord: Vector) -> None:
    actor = actors.Actor("Swordsman", coord, SpriteType.A_SWORDSMAN)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_paladin(coord: Vector) -> None:
    actor = actors.Actor("Paladin", coord, SpriteType.A_PALADIN)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_goblin(coord: Vector) -> None:
    actor = actors.Actor("Goblin", coord, SpriteType.A_GOBLIN)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_goblin_archer(coord: Vector) -> None:
    actor = actors.Actor("Goblin Archer", coord, SpriteType.A_GOBLIN_ARCHER)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_goblin_warrior(coord: Vector) -> None:
    actor = actors.Actor("Goblin Warrior", coord, SpriteType.A_GOBLIN_WARRIOR)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_goblin_noble(coord: Vector) -> None:
    actor = actors.Actor("Goblin Noble", coord, SpriteType.A_GOBLIN_NOBLE)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)


def creature_goblin_mage(coord: Vector) -> None:
    actor = actors.Actor("Goblin Mage", coord, SpriteType.A_GOBLIN_MAGE)
    creature = actors.CreatureComponent(initiative=0)
    actor.add_component(creature)
    creature_generator(actor)
