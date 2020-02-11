# game files
from bfrl import ai
from bfrl import constants
from bfrl import game
from bfrl import maps
from bfrl import menu


def cast_heal(caster, value):
    """
    Casts heals, increasing target HP by value amount. Cast cancelled if creature at Max HP.
    :param caster: Creature targeted by Heal
    :param value: Heal amount
    :return: None if successful, 'canceled' if not
    """

    if caster.creature.hp == caster.creature.max_hp:
        game.message(f'{caster.creature.name_instance} the {caster.name_object} already at max hp.')
        return 'canceled'
    else:
        caster.creature.heal(value)
        heal_value = min(value, caster.creature.max_hp - value)
        game.message(f'{caster.display_name}  healed for {heal_value} health.')
        return None


def cast_lightning(caster, value):

    spell_range, spell_range = value

    # prompt player for a tile
    origin_tile = (caster.x, caster.y)
    target_tile = menu.tile_select(origin_tile, max_range=spell_range, ignore_walls=False)

    # convert that tile into a list of tiles between player and target
    if target_tile:
        list_of_tiles = maps.find_line(origin_tile, target_tile)

        # cycle through list, damage all creatures for value
        for x, y in list_of_tiles[1:]:
            target = maps.check_for_creature(x, y)
            if target:
                game.message(f'{target.display_name} is hit by a lightning bolt and takes {spell_range} damage!')
                target.creature.take_damage(spell_range)
    else:
        print('cast lightning cancelled.')


def cast_fireball(caster, value):

    spell_damage, spell_radius, spell_range = value

    # Get target tile
    origin_tile = (caster.x, caster.y)
    target_tile = menu.tile_select(origin_tile, max_range=spell_range, ignore_walls=False, ignore_creatures=False,
                                   radius=spell_radius)

    # get sequence of tiles
    if target_tile:
        list_of_tiles = maps.find_radius(target_tile, spell_radius)

        # damage all creatures in tiles
        for x, y in list_of_tiles:
            target = maps.check_for_creature(x, y)
            if target:
                game.message(f'{target.display_name} is hit by a fireball and takes {spell_damage} damage!')
                target.creature.take_damage(spell_damage)
    else:
        print('cast lightning cancelled.')


def cast_confusion(_, effect_length):

    # get target
    target_tile = menu.tile_select()
    if target_tile:
        tx, ty = target_tile
        target = maps.check_for_creature(tx, ty)

        # temporarily confuse the target
        if target:
            o_ai = target.ai
            target.ai = ai.Confuse(old_ai=o_ai, num_turns=effect_length)
            target.ai.owner = target

            game.message(f"{target.display_name} is confused. The creature's eyes glaze over", constants.COLOR_GREEN)
