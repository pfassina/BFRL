# modules
import numpy as np
import random
import tcod

# game files
from bfrl import constants
from bfrl import globals
from bfrl import actors
from bfrl import ai
from bfrl import death
from bfrl import magic


def player(coordinates):

    x, y = coordinates

    bag = actors.ComponentContainer()
    creature_component = actors.ComponentCreature('Greg', base_attack=4, base_defense=10, death_function=death.player)

    globals.PLAYER = actors.ObjActor(x, y, 'Python', 'A_PLAYER',
                                     animation_speed=1, creature=creature_component,
                                     container=bag, depth=constants.DEPTH_PLAYER)
    globals.GAME.current_map.list_of_objects.append(globals.PLAYER)

    return globals.PLAYER


def portal(coordinates):

    x, y = coordinates
    exit_portal_component = actors.ComponentExitPortal()
    obj_exit_portal = actors.ObjActor(x, y, 'Exit Portal', animation_key='S_PORTAL_CLOSED',
                                      exit_portal=exit_portal_component, depth=constants.DEPTH_STAIRS)

    globals.GAME.current_map.list_of_objects.append(obj_exit_portal)


def lamp(coordinates):

    x, y = coordinates
    item_component = actors.ComponentItem()
    obj_lamp = actors.ObjActor(x, y, 'The Lamp', animation_key='S_MAGIC_LAMP', item=item_component)

    globals.GAME.current_map.list_of_objects.append(obj_lamp)


def stairs(coordinates, downwards=True):

    x, y = coordinates
    if downwards:
        stairs_component = actors.ComponentStairs()
        obj_stairs = actors.ObjActor(x, y, 'stairs down', animation_key='S_STAIRS_DOWN',
                                     stairs=stairs_component, depth=constants.DEPTH_STAIRS)
    else:
        stairs_component = actors.ComponentStairs(downwards)
        obj_stairs = actors.ObjActor(x, y, 'stairs up', animation_key='S_STAIRS_UP',
                                     stairs=stairs_component, depth=constants.DEPTH_STAIRS)

    globals.GAME.current_map.list_of_objects.append(obj_stairs)


# Items
def item(coordinates):

    generator_dict = {
        1: scroll_lightning(coordinates),
        2: scroll_fireball(coordinates),
        3: scroll_confusion(coordinates),
        4: weapon_sword(coordinates),
        5: armor_shield(coordinates),
    }

    # generate random item with equal probability
    random_num = random.randint(1, len(generator_dict))

    selected_item = generator_dict[random_num]
    globals.GAME.current_map.list_of_objects.append(selected_item)


def scroll_lightning(coordinates):

    x, y = coordinates

    spell_damage = tcod.random_get_int(None, 5, 7)
    spell_range = tcod.random_get_int(None, 7, 8)

    item_component = actors.ComponentItem(use_function=magic.cast_lightning, value=(spell_damage, spell_range))
    scroll = actors.ObjActor(x, y, "Lightning scroll", 'S_SCROLL_01', item=item_component, depth=constants.DEPTH_ITEMS)

    return scroll


def scroll_fireball(coordinates):

    x, y = coordinates

    spell_damage = tcod.random_get_int(None, 2, 4)
    spell_radius = 1
    spell_range = tcod.random_get_int(None, 9, 12)

    item_component = actors.ComponentItem(use_function=magic.cast_fireball,
                                          value=(spell_damage, spell_radius, spell_range))
    scroll = actors.ObjActor(x, y, "Fireball scroll", 'S_SCROLL_02', item=item_component, depth=constants.DEPTH_ITEMS)

    return scroll


def scroll_confusion(coordinates):

    x, y = coordinates

    effect_length = tcod.random_get_int(None, 5, 10)

    item_component = actors.ComponentItem(use_function=magic.cast_confusion, value=effect_length)
    scroll = actors.ObjActor(x, y, "Confusion scroll", 'S_SCROLL_03', item=item_component, depth=constants.DEPTH_ITEMS)

    return scroll


def weapon_sword(coordinates):

    x, y = coordinates

    bonus = tcod.random_get_int(None, 1, 2)

    equipment_component = actors.ComponentEquipment(attack_bonus=bonus, slot='hand_right')
    sword = actors.ObjActor(x, y, "sword", 'S_SWORD', equipment=equipment_component, depth=constants.DEPTH_ITEMS)

    return sword


def armor_shield(coordinates):

    x, y = coordinates

    bonus = tcod.random_get_int(None, 1, 2)

    equipment_component = actors.ComponentEquipment(defense_bonus=bonus, slot='hand_left')
    shield = actors.ObjActor(x, y, "shield", 'S_SHIELD', equipment=equipment_component, depth=constants.DEPTH_ITEMS)

    return shield


# Enemies
def enemy(coordinates):

    generator_dict = {
        0: snake_anaconda(coordinates),
        1: snake_cobra(coordinates),
        2: mouse(coordinates),
    }

    # Generate Random Snake based on p probability weights
    random_num = np.random.choice(len(generator_dict), p=[0.5, 0.15, 0.35])

    selected_enemy = generator_dict[random_num]
    globals.GAME.current_map.list_of_objects.append(selected_enemy)


def snake_anaconda(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic female'),
        'base_attack': tcod.random_get_int(None, 1, 2),
        'hp': tcod.random_get_int(None, 5, 10),
        'death_function': death.monster
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'anaconda',
        'animation_key': 'A_SNAKE_01',
        'animation_speed': 1,
        'depth': constants.DEPTH_CREATURES,
        'creature': actors.ComponentCreature(**creature_attributes),
        'ai': ai.Chase(),
    }

    anaconda = actors.ObjActor(**actor_attributes)

    return anaconda


def snake_cobra(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic male'),
        'base_attack': tcod.random_get_int(None, 3, 6),
        'hp': tcod.random_get_int(None, 15, 20),
        'death_function': death.monster
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'cobra',
        'animation_key': 'A_SNAKE_02',
        'animation_speed': 1,
        'depth': constants.DEPTH_CREATURES,
        'creature': actors.ComponentCreature(**creature_attributes),
        'ai': ai.Chase(),
    }

    cobra = actors.ObjActor(**actor_attributes)

    return cobra


def mouse(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic male'),
        'base_attack': 0,
        'hp': 1,
        'death_function': death.mouse
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'mouse',
        'animation_key': 'A_MOUSE_01',
        'animation_speed': 1,
        'depth': constants.DEPTH_CREATURES,
        'creature': actors.ComponentCreature(**creature_attributes),
        'ai': ai.Flee(),
        'item': actors.ComponentItem(use_function=magic.cast_heal, value=5),
    }

    cobra = actors.ObjActor(**actor_attributes)

    return cobra
