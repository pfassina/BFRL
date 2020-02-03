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
        self.explored = False


class StructureAssets:
    def __init__(self):
        
        # Sprite Sheets
        char_sprite_sheet = ObjectSpriteSheet('data/reptiles.png')
        enemies_sprite_sheet = ObjectSpriteSheet('data/aquatic_creatures.png')
        
        # Animations
        self.A_PLAYER = char_sprite_sheet.get_animation('m', 5, width=16, height=16, num_sprites=2, scale=(32, 32))
        self.A_ENEMY = enemies_sprite_sheet.get_animation('k', 1, width=16, height=16, num_sprites=2, scale=(32, 32))

        # Sprites
        self.S_WALL = pygame.image.load('data/wall.jpg')
        self.S_WALL_EXPLORED = pygame.image.load('data/wall_explored.png')

        self.S_FLOOR = pygame.image.load('data/floor.png')
        self.S_FLOOR_EXPLORED = pygame.image.load('data/floor_explored.png')

        # Fonts
        self.FONT_DEBUG_MESSAGE = pygame.font.Font('data/joystix.ttf', 16)
        self.FONT_MESSAGE_TEXT = pygame.font.Font('data/joystix.ttf', 12)


#   ______   .______          __   _______   ______ .___________.    _______.
#  /  __  \  |   _  \        |  | |   ____| /      ||           |   /       |
# |  |  |  | |  |_)  |       |  | |  |__   |  ,----'`---|  |----`  |   (----`
# |  |  |  | |   _  <  .--.  |  | |   __|  |  |         |  |        \   \
# |  `--'  | |  |_)  | |  `--'  | |  |____ |  `----.    |  |    .----)   |
#  \______/  |______/   \______/  |_______| \______|    |__|    |_______/


class ObjActor:
    def __init__(self, x, y, name_object, animation, animation_speed=0.5, creature=None, ai=None, container=None, item=None):
        self.x = x
        self.y = y
        self.animation = animation
        self.animation_speed = animation_speed / 1.0

        # animation flicker speed
        self.flicker_speed = self.animation_speed / len(self.animation)
        self.flicker_timer = 0.0
        self.sprite_image = 0

        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

    def draw(self):
        is_visible = FOV_MAP.fov[self.y, self.x]
        if is_visible:
            if len(self.animation) == 1:
                SURFACE_MAIN.blit(self.animation[0], (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT))
            elif len(self.animation) > 1:
                if CLOCK.get_fps() > 0.0:
                    self.flicker_timer += 1 / CLOCK.get_fps()
                if self.flicker_timer >= self.flicker_speed:
                    self.flicker_timer = 0.0
                    if self.sprite_image >= len(self.animation) - 1:
                        self.sprite_image = 0
                    else:
                        self.sprite_image += 1
                SURFACE_MAIN.blit(self.animation[self.sprite_image], (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT))


class ObjectGame:
    def __init__(self):
        
        self.current_map = map_create()
        self.current_objects = []
        
        self.message_history = []


class ObjectSpriteSheet:
    """
    Class used to grab images out of a sprite sheet
    """

    def __init__(self, file_name):
        # load sprite sheet
        self.sprite_sheet = pygame.image.load(file_name).convert()
        self.tile_dictionary = {
            'a': 1, 'b': 2, 'c': 3, 'd': 4,
            'e': 5, 'f': 6, 'g': 7, 'h': 8,
            'i': 9, 'j': 10, 'k': 11, 'l': 12,
            'm': 13, 'n': 14, 'o': 15, 'p': 16
        }

    def get_image(self, column, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, scale=None):
        """

        :param column:
        :param row:
        :param width:
        :param height:
        :param scale: X, Y tuple with scale parameters
        :return: list of sprites to be animated
        """

        sprite_list = []

        image = pygame.Surface([width, height]).convert()
        image.blit(self.sprite_sheet, (0, 0), (self.tile_dictionary[column] * width, row * height, width, height))
        image.set_colorkey(constants.COLOR_BLACK)

        if scale:
            (new_width, new_height) = scale
            image = pygame.transform.scale(image, (new_width, new_height))

        sprite_list.append(image)

        return sprite_list

    def get_animation(self, column, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, num_sprites=1, scale=None):
        """

        :param column:
        :param row:
        :param width:
        :param height:
        :param num_sprites: number of sprites on an animation
        :param scale: X, Y tuple with scale parameters
        :return: list of sprites to be animated
        """

        sprite_list = []
        for i in range(num_sprites):

            # create blank image
            image = pygame.Surface([width, height]).convert()

            # copy image from sheet onto blank
            image.blit(self.sprite_sheet, (0, 0), (self.tile_dictionary[column] * width + width * i, row * height, width, height))

            # set transparency key to black
            image.set_colorkey(constants.COLOR_BLACK)

            if scale:
                (new_width, new_height) = scale
                image = pygame.transform.scale(image, (new_width, new_height))

            sprite_list.append(image)

        return sprite_list


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

        tile_is_wall = (GAME.current_map[self.owner.x + dx][self.owner.y + dy].block_path is True)

        target = map_check_for_creatures(self.owner.x + dx, self.owner.y + dy, self.owner)
        if target:
            self.attack(target, 2)

        if not tile_is_wall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target, damage):
        message = f'{self.name_instance} attacks {target.creature.name_instance} for {damage} damage!'
        game_message(message, constants.COLOR_RED)
        target.creature.take_damage(damage)

    def take_damage(self, damage):
        self.hp -= damage
        message = f"{self.name_instance}'s health is {self.hp}/{self.max_hp}"
        game_message(message, constants.COLOR_WHITE)

        if self.hp <= 0:
            if self.death_function is not None:
                self.death_function(self.owner)


class ComponentContainer:
    def __init__(self, volume=10.0, inventory=[]):
        self.max_volume = volume
        self.inventory = inventory

    # get names of everything in inventory
    # get volume within container
    @property
    def volume(self):
        return 0.0
    # get the weight of everything within container


class ComponentItem:
    def __init__(self, weight=0.0, volume=0.0):
        self.weight = weight
        self.volume = volume

    def pick_up(self, actor):
        if actor.container:
            if actor.container.volume + self.volume > actor.container.max_volume:
                game_message('Not enough room to pick up', color=constants.COLOR_RED)
            else:
                game_message('Picking up')
                actor.container.inventory.append(self.owner)
                GAME.current_objects.remove(self.owner)
                self.container = actor.container

    def drop(self, new_x, new_y):
        GAME.current_objects.append(self.owner)
        self.container.inventory.remove(self.owner)
        self.owner.x = new_x
        self.owner.y = new_y
        game_message('Item dropped!')

    # use this item

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

    message = f'{monster.creature.name_instance} is dead!'
    game_message(message, constants.COLOR_GREY)
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

    map_make_fov(new_map)

    return new_map


def map_check_for_creatures(x, y, exclude_object=None):

    target = None
    if exclude_object:
        for obj in GAME.current_objects:
            if (obj is not exclude_object
                    and obj.x == x
                    and obj.y == y
                    and obj.creature):
                target = obj

            if target:
                return target


def map_make_fov(incoming_map):

    global FOV_MAP
    FOV_MAP = tcod.map.Map(constants.MAP_WIDTH, constants.MAP_HEIGHT)

    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
            if incoming_map[x][y].block_path:
                FOV_MAP.transparent[y, x] = False
                FOV_MAP.walkable[y, x] = False
            else:
                FOV_MAP.transparent[y, x] = True
                FOV_MAP.walkable[y, x] = True


def map_calculate_fov():

    global FOV_CALCULATE
    if FOV_CALCULATE:
        FOV_CALCULATE = False
        FOV_MAP.compute_fov(PLAYER.x, PLAYER.y, constants.TORCH_RADIUS, constants.FOV_LIGHT_WALLS,
                            constants.FOV_ALGORITHM)


def map_objects_at_coordinates(x, y):

    object_options = [obj for obj in GAME.current_objects if obj.x == x and obj.y == y]
    return object_options


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
    draw_map(GAME.current_map)

    # draw the characters
    for obj in GAME.current_objects:
        obj.draw()

    draw_debug()
    draw_messages()

    # update the display
    pygame.display.flip()


def draw_map(map_to_draw):

    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):

            is_visible = FOV_MAP.fov[y, x]
            if is_visible:

                map_to_draw[x][y].explored = True
                if map_to_draw[x][y].block_path:
                    SURFACE_MAIN.blit(ASSETS.S_WALL, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(ASSETS.S_FLOOR, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))

            elif map_to_draw[x][y].explored:
                if map_to_draw[x][y].block_path:
                    SURFACE_MAIN.blit(ASSETS.S_WALL_EXPLORED, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(ASSETS.S_FLOOR_EXPLORED, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))


def draw_debug():
    draw_text(SURFACE_MAIN, f'FPS: {int(CLOCK.get_fps())}', (0, 0), constants.COLOR_WHITE, constants.COLOR_BLACK)


def draw_messages():

    if len(GAME.message_history) <= constants.NUM_MESSAGES:
        to_draw = GAME.message_history
    else:
        to_draw = GAME.message_history[-constants.NUM_MESSAGES:]

    text_height = helper_text_height(ASSETS.FONT_MESSAGE_TEXT)

    start_y = constants.MAP_HEIGHT * constants.CELL_HEIGHT - (constants.NUM_MESSAGES * text_height) - 10

    for index, (message, color) in enumerate(to_draw):
        draw_text(SURFACE_MAIN, message, (0, start_y + index * text_height), color, constants.COLOR_BLACK)


def draw_text(display_surface, text_to_display, coordinates, text_color, back_color=None):
    """
    This function takes in some text, and display it on the referenced surfaced
    :param display_surface: Surface to display text
    :param text_to_display: Text to be displayed
    :param coordinates: Coordinates tuple
    :param text_color: Text color
    :param back_color: Text background color
    """

    text_surface, text_rectangle = helper_text_objects(text_to_display, text_color, back_color)
    text_rectangle.topleft = coordinates
    display_surface.blit(text_surface, text_rectangle)


#  __    __   _______  __      .______    _______ .______          _______.
# |  |  |  | |   ____||  |     |   _  \  |   ____||   _  \        /       |
# |  |__|  | |  |__   |  |     |  |_)  | |  |__   |  |_)  |      |   (----`
# |   __   | |   __|  |  |     |   ___/  |   __|  |      /        \   \    
# |  |  |  | |  |____ |  `----.|  |      |  |____ |  |\  \----.----)   |   
# |__|  |__| |_______||_______|| _|      |_______|| _| `._____|_______/    


def helper_text_objects(incoming_text, incoming_color, incoming_background):

    if incoming_background:
        text_surface = ASSETS.FONT_DEBUG_MESSAGE.render(incoming_text, False, incoming_color, incoming_background)
    else:
        text_surface = ASSETS.FONT_DEBUG_MESSAGE.render(incoming_text, False, incoming_color)

    return text_surface, text_surface.get_rect()


def helper_text_height(font):
    """
    Return the Height of a font in pixels
    :param font: font to be examined
    :return: font height in pixels
    """

    font_object = font.render('a', False, (0, 0, 0))
    font_rect = font_object.get_rect()

    return font_rect.height


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
        map_calculate_fov()

        if player_action == 'QUIT':
            game_quit = True

        elif player_action != 'no-action':
            for obj in GAME.current_objects:
                if obj.ai:
                    obj.ai.take_turn()

        # draw the game
        draw_game()

        CLOCK.tick(constants.GAME_FPS)

    # quit the game
    pygame.quit()
    exit()


def game_initialize():
    """
    Initializes the main window and pygame
    """

    global SURFACE_MAIN, GAME, CLOCK, FOV_CALCULATE, PLAYER, ENEMY, ASSETS

    # initialize pygame
    pygame.init()

    SURFACE_MAIN = pygame.display.set_mode((
            constants.MAP_WIDTH * constants.CELL_WIDTH,
            constants.MAP_HEIGHT * constants.CELL_HEIGHT
        ))

    GAME = ObjectGame()

    CLOCK = pygame.time.Clock()

    FOV_CALCULATE = True
    
    ASSETS = StructureAssets()

    container_com1 = ComponentContainer()
    creature_comp1 = ComponentCreature('greg')
    PLAYER = ObjActor(1, 1, 'Python', ASSETS.A_PLAYER, animation_speed=1, creature=creature_comp1, container=container_com1)

    item_com1 = ComponentItem()
    creature_comp2 = ComponentCreature('jack', death_function=death_monster)
    ai_com = AITest()
    ENEMY = ObjActor(15, 15, 'Crab', ASSETS.A_ENEMY, animation_speed=1, creature=creature_comp2, ai=ai_com, item=item_com1)

    GAME.current_objects = [PLAYER, ENEMY]


def game_handle_keys():

    global FOV_CALCULATE

    # get player input
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            return 'QUIT'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                PLAYER.creature.move(0, -1)
                FOV_CALCULATE = True
                return 'player-moved'
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                FOV_CALCULATE = True
                return 'player-moved'
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                FOV_CALCULATE = True
                return 'player-moved'
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                FOV_CALCULATE = True
                return 'player-moved'
            if event.key == pygame.K_g:
                objects_at_player = map_objects_at_coordinates(PLAYER.x, PLAYER.y)
                for obj in objects_at_player:
                    if obj.item:
                        obj.item.pick_up(PLAYER)
            if event.key == pygame.K_d:
                if len(PLAYER.container.inventory) > 0:
                    PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)

    return 'no-action'


def game_message(message, color=constants.COLOR_GREY):
    GAME.message_history.append((message, color))


if __name__ == '__main__':
    game_initialize()
    game_main_loop()
