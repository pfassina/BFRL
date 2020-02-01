import tcod
import pygame

import constants

#      _______.___________..______       __    __    ______ .___________.
#     /       |           ||   _  \     |  |  |  |  /      ||           |
#    |   (----`---|  |----`|  |_)  |    |  |  |  | |  ,----'`---|  |----`
#     \   \       |  |     |      /     |  |  |  | |  |         |  |
# .----)   |      |  |     |  |\  \----.|  `--'  | |  `----.    |  |
# |_______/       |__|     | _| `._____| \______/   \______|    |__|


class StructureTile:
    def __init__(self, block_path):
        self.block_path = block_path


#   ______   .______          __   _______   ______ .___________.    _______.
#  /  __  \  |   _  \        |  | |   ____| /      ||           |   /       |
# |  |  |  | |  |_)  |       |  | |  |__   |  ,----'`---|  |----`  |   (----`
# |  |  |  | |   _  <  .--.  |  | |   __|  |  |         |  |        \   \
# |  `--'  | |  |_)  | |  `--'  | |  |____ |  `----.    |  |    .----)   |
#  \______/  |______/   \______/  |_______| \______|    |__|    |_______/


class ObjActor:
    def __init__(self, x, y, name_object, sprite, creature=None, ai=None):
        self.x = x
        self.y = y
        self.sprite = sprite

        self.creature = creature
        if creature:
            self.creature = creature
            creature.owner = self

        self.ai = ai
        if ai:
            self.ai = ai
            ai.owner = self

    def draw(self):
        SURFACE_MAIN.blit(self.sprite, (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT))




#   ______   ______   .___  ___. .______     ______   .__   __.  _______ .__   __. .___________.    _______.
#  /      | /  __  \  |   \/   | |   _  \   /  __  \  |  \ |  | |   ____||  \ |  | |           |   /       |
# |  ,----'|  |  |  | |  \  /  | |  |_)  | |  |  |  | |   \|  | |  |__   |   \|  | `---|  |----`  |   (----`
# |  |     |  |  |  | |  |\/|  | |   ___/  |  |  |  | |  . `  | |   __|  |  . `  |     |  |        \   \
# |  `----.|  `--'  | |  |  |  | |  |      |  `--'  | |  |\   | |  |____ |  |\   |     |  |    .----)   |
#  \______| \______/  |__|  |__| | _|       \______/  |__| \__| |_______||__| \__|     |__|    |_______/


class ComponentCreature:
    """
    Creatures have health, can die, and can damage other objects by attacking them.
    """

    def __init__(self, name_instance, hp=10, death_function=None):
        self.name_instance = name_instance
        self.max_hp = hp
        self.hp = hp
        self.death_function = death_function

    def move(self, dx, dy):

        tile_is_wall = (GAME_MAP[self.owner.x + dx][self.owner.y + dy].block_path is True)

        target = map_check_for_creatures(self.owner.x + dx, self.owner.y + dy, self.owner)
        if target:
            self.attack(target, 2)

        if not tile_is_wall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target, damage):
        print(f'{self.name_instance} attacks {target.creature.name_instance} for {damage} damage!')
        target.creature.take_damage(damage)

    def take_damage(self, damage):
        self.hp -= damage
        print(f"{self.name_instance}'s health is {self.hp}/{self.max_hp}")

        if self.hp <= 0:
            if self.death_function is not None:
                self.death_function(self.owner)

class ComponentItem:
    pass


class ComponentContainer:
    pass


#      ___       __
#     /   \     |  |
#    /  ^  \    |  |
#   /  /_\  \   |  |
#  /  _____  \  |  |
# /__/     \__\ |__|


class AITest:
    """
    Once per turn, execute.
    """

    def take_turn(self):
        self.owner.creature.move(tcod.random_get_int(None, -1, 1), tcod.random_get_int(None, -1, 1))


def death_monster(monster):
    """
    On death, most monsters stop moving.
    :param monster: Monster instance
    """

    print(f'{monster.creature.name_instance} is dead!')
    monster.creature = None
    monster.ai = None


# .___  ___.      ___      .______
# |   \/   |     /   \     |   _  \
# |  \  /  |    /  ^  \    |  |_)  |
# |  |\/|  |   /  /_\  \   |   ___/
# |  |  |  |  /  _____  \  |  |
# |__|  |__| /__/     \__\ | _|


def map_create():
    new_map = [[StructureTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    new_map[10][10].block_path = True
    new_map[10][15].block_path = True

    for x in range(constants.MAP_WIDTH):
        new_map[x][0].block_path = True
        new_map[x][constants.MAP_HEIGHT - 1].block_path = True

    for y in range(constants.MAP_HEIGHT):
        new_map[0][y].block_path = True
        new_map[constants.MAP_HEIGHT - 1][y].block_path = True

    return new_map


def map_check_for_creatures(x, y, exclude_object=None):

    target = None
    if exclude_object:
        for obj in GAME_OBJECTS:
            if (obj is not exclude_object
                    and obj.x == x
                    and obj.y == y
                    and obj.creature):
                target = obj

            if target:
                return target

#  _______  .______          ___   ____    __    ____  __  .__   __.   _______
# |       \ |   _  \        /   \  \   \  /  \  /   / |  | |  \ |  |  /  _____|
# |  .--.  ||  |_)  |      /  ^  \  \   \/    \/   /  |  | |   \|  | |  |  __
# |  |  |  ||      /      /  /_\  \  \            /   |  | |  . `  | |  | |_ |
# |  '--'  ||  |\  \----./  _____  \  \    /\    /    |  | |  |\   | |  |__| |
# |_______/ | _| `._____/__/     \__\  \__/  \__/     |__| |__| \__|  \______|
#


def draw_game():

    global SURFACE_MAIN

    # clear the surface
    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)

    # draw the map
    draw_map(GAME_MAP)

    # draw the characters
    for obj in GAME_OBJECTS:
        obj.draw()

    # update the display
    pygame.display.flip()


def draw_map(map_to_draw):

    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):
            if map_to_draw[x][y].block_path:
                SURFACE_MAIN.blit(constants.S_WALL, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))
            else:
                SURFACE_MAIN.blit(constants.S_FLOOR, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))

#   _______      ___      .___  ___.  _______
#  /  _____|    /   \     |   \/   | |   ____|
# |  |  __     /  ^  \    |  \  /  | |  |__
# |  | |_ |   /  /_\  \   |  |\/|  | |   __|
# |  |__| |  /  _____  \  |  |  |  | |  |____
#  \______| /__/     \__\ |__|  |__| |_______|
#


def game_main_loop():
    """
    Runs the game main loop
    """
    game_quit = False
    while not game_quit:

        # Handle Player Input
        player_action = game_handle_keys()
        if player_action == 'QUIT':
            game_quit = True

        elif player_action != 'no-action':
            for obj in GAME_OBJECTS:
                if obj.ai:
                    obj.ai.take_turn()

        # draw the game
        draw_game()

    # quit the game
    pygame.quit()
    exit()


def game_initialize():
    """
    Initializes the main window and pygame
    """

    global SURFACE_MAIN, GAME_MAP, PLAYER, ENEMY, GAME_OBJECTS

    # initialize pygame
    pygame.init()
    SURFACE_MAIN = pygame.display.set_mode((
            constants.MAP_WIDTH * constants.CELL_WIDTH,
            constants.MAP_HEIGHT * constants.CELL_HEIGHT
        ))

    GAME_MAP = map_create()

    creature_comp1 = ComponentCreature('greg')
    PLAYER = ObjActor(1, 1, 'Python', constants.S_PLAYER, creature=creature_comp1)

    creature_comp2 = ComponentCreature('jack', death_function=death_monster)
    ai_com = AITest()
    ENEMY = ObjActor(15, 15, 'Crab', constants.S_ENEMY, creature=creature_comp2, ai=ai_com)

    GAME_OBJECTS = [PLAYER, ENEMY]


def game_handle_keys():

    # get player input
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            return 'QUIT'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                PLAYER.creature.move(0, -1)
                return 'player-moved'
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                return 'player-moved'
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                return 'player-moved'
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                return 'player-moved'
    return 'no-action'


if __name__ == '__main__':
    game_initialize()
    game_main_loop()
