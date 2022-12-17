# modules
import tcod

# game files
from bfrl import globals
from bfrl import constants
from bfrl import game


class Confuse:
    """
    Once per turn, creature moves randomly, until confuse wears off.
    """

    def __init__(self, old_ai, num_turns):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):

        if self.num_turns > 0:
            self.owner.creature.move(tcod.random_get_int(None, -1, 1), tcod.random_get_int(None, -1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            game.message(f'{self.owner.display_name} has broken free!', constants.COLOR_RED)


class Chase:
    """
    Basic monster AI which chases and tries to harm the player
    """

    def take_turn(self):

        monster = self.owner
        if globals.FOV_MAP.fov[monster.y, monster.x]:
            # Moves towards the player if far away
            if monster.distance_to(globals.PLAYER) >= 2:
                monster.move_towards(globals.PLAYER)
            # If close enough, attack player
            elif globals.PLAYER.creature.hp > 0:
                monster.creature.attack(globals.PLAYER)


class Flee:
    """
    Basic monster AI which flees from the player
    """

    def take_turn(self):
        monster = self.owner
        if globals.FOV_MAP.fov[monster.y, monster.x]:
            monster.move_away(globals.PLAYER)
