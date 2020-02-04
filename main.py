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
    """
    This class functions as a struct that tracks the data for each
    tile within a map.

    ** PROPERTIES **
    StructureTile.block_path : TRUE if tile prevents actors from moving through it under normal circumstances.
    StructureTile.explored : Initializes to FALSE, set to true if player has seen it before.
    """

    def __init__(self, block_path):
        self.block_path = block_path
        self.explored = False


class StructureAssets:
    """
    This class is a structure that holds all assets used in the game. This includes sprites, sound effects, and music.
    """

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


#   ______   .______          __   _______   ______ .___________.    _______.
#  /  __  \  |   _  \        |  | |   ____| /      ||           |   /       |
# |  |  |  | |  |_)  |       |  | |  |__   |  ,----'`---|  |----`  |   (----`
# |  |  |  | |   _  <  .--.  |  | |   __|  |  |         |  |        \   \
# |  `--'  | |  |_)  | |  `--'  | |  |____ |  `----.    |  |    .----)   |
#  \______/  |______/   \______/  |_______| \______|    |__|    |_______/


class ObjActor:
    """
    The actor object represents every entity in the game that 'interacts' with the player or the environment
    in some way. It is made up of components which alter an actors behavior.

    ** PROPERTIES **
    ObjActor.flicker_speed : represents the conversion of animation length in seconds to number of frames
    ObjActor.flicker_timer : the current counter until the next frame of the animation should be displayed.
    ObjActor.sprite_image : the index location of the current image of the animation that is being displayed.

    ** METHODS **
    obj_Actor.draw() : this method draws the object to the screen.
    """
    def __init__(self, x, y, name_object, animation, animation_speed=0.5, creature=None, ai=None, container=None, item=None):
        """
        :param x: starting x position on the current map
        :param y: starting y position on the current map
        :param name_object: string containing the name of the object, "chair" or "goblin" for example.
        :param animation: A list of images that make up the object's sprite sheet. Created with StructureAssets class.
        :param animation_speed: Time in seconds it takes to loop through the object animation.
        :param creature: any object that has health, and generally can fight
        :param ai: ai is a component that executes an action every time the object is able to act
        :param container: containers are objects that can hold an inventory
        :param item: items are items that are able to be picked up and used
        """

        self.x = x
        self.y = y

        self.name_object = name_object

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
        """draws the obj_Actor to the screen"""
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
                draw_location = (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT)
                SURFACE_MAIN.blit(self.animation[self.sprite_image], draw_location)


class ObjectGame:
    """
    The obj_Game is an object that stores all the information used by the game to 'keep track' of progress.
    It will track maps, object lists, and game history or record of messages.

    ** PROPERTIES **
    ObjectGame.current_map : whatever map is currently loaded.
    ObjectGame.current_objects : list of objects for the current map.
    ObjectGame.message_history : list of messages that have been pushed to the player over the course of a game.
    """

    def __init__(self):
        
        self.current_map = map_create()
        self.current_objects = []
        
        self.message_history = []


class ObjectSpriteSheet:
    """
    Class used to grab images out of a sprite sheet. As a class, it allows you to access and subdivide portions of the
    sprite_sheet.

    ** PROPERTIES **
    ObjectSpriteSheet.sprite_sheet : The loaded spritesheet accessed through the file_name argument.
    """

    def __init__(self, file_name):
        """
        :param file_name: String which contains the directory/filename of the image for use as a spritesheet.
        """
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
        returns a list containing a single image from a spritesheet given a grid location.
        :param column: Letter which gets converted into an integer
        :param row: integer
        :param width: integer, individual image width in pixels
        :param height: integer, individual sprite height in pixels
        :param scale: Tuple (width, height).  If included, scales the images to a new size
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
        returns a list containing a sequence of images starting from a grid location.
        :param column: Letter which gets converted into an integer
        :param row: integer
        :param width: integer, individual image width in pixels
        :param height: integer, individual sprite height in pixels
        :param num_sprites: number of sprites on an animation
        :param scale: Tuple (width, height).  If included, scales the images to a new size
        :return: list of sprites to be animated
        """

        sprite_list = []
        for i in range(num_sprites):

            # create blank image
            image = pygame.Surface([width, height]).convert()

            # copy image from sheet onto blank
            sprite_location_on_sheet = (self.tile_dictionary[column] * width + width * i, row * height, width, height)
            image.blit(self.sprite_sheet, (0, 0), sprite_location_on_sheet)

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
    Creatures have health, and can damage other objects by attacking them.  Can also die.

    ** METHODS **
    *************
    com_Creature.move : .

    com_Creature.attack : allows the creature to attack a target.

    com_Creature.take_damage : Creature takes damage, and if the
    creature's health falls below 0, executes the death function.
    """

    def __init__(self, name_instance, hp=10, death_function=None):
        """

        :param name_instance: String, name of specific object. "Bob" for example.
        :param hp: integer, health of the creature. Is converted into both the maximum health and the current health.
        :param death_function: function that is executed whenever the creature's health dips below 0.
        """
        self.name_instance = name_instance
        self.max_hp = hp
        self.hp = hp
        self.death_function = death_function

    def move(self, dx, dy):
        """
        Attempts to move the object in a specific direction
        :param dx: difference of x from current location
        :param dy: difference of y from current location
        """

        tile_is_wall = (GAME.current_map[self.owner.x + dx][self.owner.y + dy].block_path is True)

        target = map_check_for_creature(self.owner.x + dx, self.owner.y + dy, self.owner)
        if target:
            self.attack(target, 2)

        if not tile_is_wall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target, damage):
        """
        Allows the creature to attack a target
        :param target: object attacked by the creature
        :param damage: damage of the attack
        """
        message = f'{self.name_instance} attacks {target.creature.name_instance} for {damage} damage!'
        game_message(message, constants.COLOR_RED)
        target.creature.take_damage(damage)

    def take_damage(self, damage):
        """
        Creature takes damage, and if the creature's health falls below 0, executes the death function.
        :param damage: damage taken by the creature
        """
        self.hp -= damage
        message = f"{self.name_instance}'s health is {self.hp}/{self.max_hp}"
        game_message(message, constants.COLOR_WHITE)

        if self.hp <= 0:
            if self.death_function is not None:
                self.death_function(self.owner)

    def heal(self, value):
        """
        Creature heals hp.
        :param value: HP healed by the creature
        """

        if self.hp + value >= self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += value


class ComponentContainer:
    def __init__(self, volume=10.0, inventory=None):

        self.max_volume = volume
        if inventory is None:
            inventory = []
        self.inventory = inventory

    # get names of everything in inventory
    # get volume within container
    @property
    def volume(self):
        return 0.0
    # get the weight of everything within container


class ComponentItem:
    def __init__(self, weight=0.0, volume=0.0, use_function=None, value=None):
        self.weight = weight
        self.volume = volume
        self.use_function = use_function
        self.value = value

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

    def use(self):

        # Use the item by production an effect and removing it
        if self.use_function:
            result = self.use_function(self.container.owner, self.value)
            if result is not None:
                print('use_function_failed')
            else:
                self.container.inventory.remove(self.owner)


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


def map_check_for_creature(x, y, exclude_object=None):
    """
    Check for creature on target tile. Returns creature owner if found.
    :param x: tile x coordinate
    :param y: tile y coordinate
    :param exclude_object: whether an object should be ignored from check.
    :return: creature owner object on tile. None if no creature on tile.
    """

    target = None
    if exclude_object:
        for obj in GAME.current_objects:
            if obj is not exclude_object and obj.x == x and obj.y == y and obj.creature:
                target = obj
    else:
        for obj in GAME.current_objects:
            if obj.x == x and obj.y == y and obj.creature:
                target = obj

    return target



def map_check_for_wall(x, y):
    """
    Checks if tile is wall
    :param x: tile x coordinate
    :param y: tile y coordinate
    :return: True if wall
    """

    return GAME.current_map[x][y].block_path


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


def map_find_line(origin_coordinates, destination_coordinates):
    """
    Converts two coordinates into a list of titles.
    :param origin_coordinates: (x1, y1)
    :param destination_coordinates: (x2, y2)
    :return: list of coordinates between coordinates 1 and coordinates 2.
    """

    x1, y1 = origin_coordinates
    x2, y2 = destination_coordinates

    coordinate_list = list(tcod.line_iter(x1, y1, x2, y2))
    return coordinate_list


def map_find_radius(coordinates, radius):
    """
    Returns all tiles within a radius of a center tile
    :param coordinates: center tile (x, y) tuple
    :param radius: radius length
    :return: list of tiles within radius of center tile
    """

    center_x, center_y = coordinates
    tile_list = []
    for x in range(center_x - radius, center_x + radius + 1):
        for y in range(center_y - radius, center_y + radius + 1):
            tile_list.append((x, y))

    return tile_list

#  _______  .______          ___   ____    __    ____  __  .__   __.   _______
# |       \ |   _  \        /   \  \   \  /  \  /   / |  | |  \ |  |  /  _____|
# |  .--.  ||  |_)  |      /  ^  \  \   \/    \/   /  |  | |   \|  | |  |  __
# |  |  |  ||      /      /  /_\  \  \            /   |  | |  . `  | |  | |_ |
# |  '--'  ||  |\  \----./  _____  \  \    /\    /    |  | |  |\   | |  |__| |
# |_______/ | _| `._____/__/     \__\  \__/  \__/     |__| |__| \__|  \______|
#


def draw_game():

    # global SURFACE_MAIN

    # clear the surface
    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)

    # draw the map
    draw_map(GAME.current_map)

    # draw the characters
    for obj in GAME.current_objects:
        obj.draw()

    draw_debug()
    draw_messages()


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
    debug_message = f'FPS: {int(CLOCK.get_fps())}'
    font_color = constants.COLOR_WHITE
    bg_color = constants.COLOR_BLACK
    draw_text(SURFACE_MAIN, debug_message, constants.FONT_DEBUG_MESSAGE, (0, 0), font_color, bg_color)


def draw_messages():

    if len(GAME.message_history) <= constants.NUM_MESSAGES:
        to_draw = GAME.message_history
    else:
        to_draw = GAME.message_history[-constants.NUM_MESSAGES:]

    text_height = helper_text_height(constants.FONT_MESSAGE_TEXT)

    start_y = constants.MAP_HEIGHT * constants.CELL_HEIGHT - (constants.NUM_MESSAGES * text_height) - 10

    for index, (message, color) in enumerate(to_draw):
        message_location = (0, start_y + index * text_height)
        draw_text(SURFACE_MAIN, message, constants.FONT_MESSAGE_TEXT, message_location, color, constants.COLOR_BLACK)


def draw_text(display_surface, text_to_display, font, coordinates, text_color, back_color=None):

    """
    This function takes in some text, and display it on the referenced surfaced
    :param display_surface: Surface to display text
    :param text_to_display: Text to be displayed
    :param font: font of the text
    :param coordinates: Coordinates tuple
    :param text_color: Text color
    :param back_color: Text background color
    """

    text_surface, text_rectangle = helper_text_objects(text_to_display, font, text_color, back_color)
    text_rectangle.topleft = coordinates
    display_surface.blit(text_surface, text_rectangle)


def draw_tile_rect(coordinates, tile_color=None, tile_alpha=150):

    x, y = coordinates
    new_x = x * constants.CELL_WIDTH
    new_y = y * constants.CELL_HEIGHT

    if tile_color:
        local_color = tile_color
    else:
        local_color = constants.COLOR_WHITE

    new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
    new_surface.fill(local_color)
    new_surface.set_alpha(tile_alpha)

    # SURFACE_MAIN
    SURFACE_MAIN.blit(new_surface, (new_x, new_y))


#  __    __   _______  __      .______    _______ .______          _______.
# |  |  |  | |   ____||  |     |   _  \  |   ____||   _  \        /       |
# |  |__|  | |  |__   |  |     |  |_)  | |  |__   |  |_)  |      |   (----`
# |   __   | |   __|  |  |     |   ___/  |   __|  |      /        \   \    
# |  |  |  | |  |____ |  `----.|  |      |  |____ |  |\  \----.----)   |   
# |__|  |__| |_______||_______|| _|      |_______|| _| `._____|_______/    


def helper_text_objects(incoming_text, incoming_font, incoming_color, incoming_background):

    if incoming_background:
        text_surface = incoming_font.render(incoming_text, False, incoming_color, incoming_background)
    else:
        text_surface = incoming_font.render(incoming_text, False, incoming_color)

    return text_surface, text_surface.get_rect()


def helper_text_height(font):
    """
    Returns the Height of a font in pixels
    :param font: font to be examined
    :return: font height in pixels
    """

    font_object = font.render('a', False, (0, 0, 0))
    font_rect = font_object.get_rect()

    return font_rect.height


def helper_text_width(font):
    """
    Returns the width of a font in pixels
    :param font: font to be examined
    :return: font height in pixels
    """

    font_object = font.render('a', False, (0, 0, 0))
    font_rect = font_object.get_rect()

    return font_rect.width


# .___  ___.      ___       _______  __    ______
# |   \/   |     /   \     /  _____||  |  /      |
# |  \  /  |    /  ^  \   |  |  __  |  | |  ,----'
# |  |\/|  |   /  /_\  \  |  | |_ | |  | |  |
# |  |  |  |  /  _____  \ |  |__| | |  | |  `----.
# |__|  |__| /__/     \__\ \______| |__|  \______|


def cast_heal(target, value):
    """
    Casts heals, increasing target HP by value amount. Cast cancelled if creature at Max HP.
    :param target: Creature targeted by Heal
    :param value: Heal amount
    :return: None if successful, 'canceled' if not
    """

    if target.creature.hp == target.creature.max_hp:
        game_message(f'{target.creature.name_instance} the {target.name_object} already at max hp.')
        return 'canceled'
    else:
        target.creature.heal(value)
        heal_value = min(value, target.creature.max_hp - value)
        game_message(f'{target.creature.name_instance} the {target.name_object} healed for {heal_value} health.')
        return None


def cast_lightning():

    damage = 5
    max_range = 5

    # prompt player for a tile
    origin_tile = (PLAYER.x, PLAYER.y)
    target_tile = menu_tile_select(origin_tile, max_range=max_range, ignore_walls=False)

    # convert that tile into a list of tiles between player and target
    if target_tile:
        list_of_tiles = map_find_line(origin_tile, target_tile)

    # cycle through list, damage all creatures for value
        for x, y in list_of_tiles[1:]:
            target = map_check_for_creature(x, y)
            if target:
                target.creature.take_damage(damage)
                game_message(f'{target.creature.name_instance} is hit by a lightning bolt and takes {damage} damage!')
    else:
        print('cast lightning cancelled.')


def cast_fireball():

    dmg = 5
    rd = 1
    rg = 4

    # Get target tile
    origin_tile = (PLAYER.x, PLAYER.y)
    target_tile = menu_tile_select(origin_tile, max_range=rg, ignore_walls=False, ignore_creatures=False, radius=rd)

    # get sequence of tiles
    if target_tile:
        list_of_tiles = map_find_radius(target_tile, rd)

        # damage all creatures in tiles
        for x, y in list_of_tiles:
            target = map_check_for_creature(x, y)
            if target:
                target.creature.take_damage(dmg)
                game_message(f'{target.name_object} is hit by a fireball and takes {dmg} damage!')
    else:
        print('cast lightning cancelled.')


# .___  ___.  _______ .__   __.  __    __       _______.
# |   \/   | |   ____||  \ |  | |  |  |  |     /       |
# |  \  /  | |  |__   |   \|  | |  |  |  |    |   (----`
# |  |\/|  | |   __|  |  . `  | |  |  |  |     \   \
# |  |  |  | |  |____ |  |\   | |  `--'  | .----)   |
# |__|  |__| |_______||__| \__|  \______/  |_______/


def menu_pause():
    """
    This menu pauses the game and displays a simple message
    """

    menu_close = False

    window_width = constants.MAP_WIDTH * constants.CELL_WIDTH
    window_height = constants.MAP_HEIGHT * constants.CELL_HEIGHT

    menu_text = 'PAUSED'
    menu_font = constants.FONT_DEBUG_MESSAGE

    text_height = helper_text_height(menu_font)
    text_width = helper_text_width(menu_font) * len(menu_text)

    text_location = (int(window_width/2 - text_width/2), int(window_height/2 - text_height/2))

    while not menu_close:
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    menu_close = True
                if event.key == pygame.K_ESCAPE:
                    menu_close = True

        font_color = constants.COLOR_WHITE
        bg_color = constants.COLOR_BLACK
        draw_text(SURFACE_MAIN, menu_text, constants.FONT_DEBUG_MESSAGE, text_location, font_color, bg_color)
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()


def menu_inventory():

    menu_close = False

    menu_width = 200
    menu_height = 200

    window_width = constants.MAP_WIDTH * constants.CELL_WIDTH
    window_height = constants.MAP_HEIGHT * constants.CELL_HEIGHT

    menu_x = int(window_width/2 - menu_width/2)
    menu_y = int(window_height/2 - menu_height/2)

    menu_location = (menu_x, menu_y)

    menu_font = constants.FONT_MESSAGE_TEXT
    menu_text_height = helper_text_height(menu_font)

    inventory_surface = pygame.Surface((menu_width, menu_height))

    while not menu_close:

        menu_font = constants.FONT_MESSAGE_TEXT
        menu_font_color = constants.COLOR_WHITE
        menu_bg_color = constants.COLOR_BLACK
        menu_mouse_over_bg = constants.COLOR_GREY

        # Clear the menu
        inventory_surface.fill(constants.COLOR_BLACK)

        # Collect list of item names
        item_list = [item.name_object for item in PLAYER.container.inventory]

        # Get list of input events
        events_list = pygame.event.get()

        # Get mouse coordinates relative to inventory window
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x_relative = mouse_x - menu_x
        mouse_y_relative = mouse_y - menu_y

        # Check if mouse is in the window
        mouse_in_window = (0 < mouse_x_relative < menu_width and 0 < mouse_y_relative < menu_height)

        # convert mouse height to inventory line
        mouse_line_selection = int(mouse_y_relative / menu_text_height)

        for event in events_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    menu_close = True
                if event.key == pygame.K_ESCAPE:
                    menu_close = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and mouse_in_window and mouse_line_selection <= len(item_list):
                    PLAYER.container.inventory[mouse_line_selection].item.use()

        # Draw item list
        for line, name in enumerate(item_list):
            name_location = (0, 0 + line * menu_text_height)
            if line == mouse_line_selection and mouse_in_window:
                draw_text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_mouse_over_bg)
            else:
                draw_text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_bg_color)

        # Display Menu
        SURFACE_MAIN.blit(inventory_surface, menu_location)
        pygame.display.flip()


def menu_tile_select(origin=None, max_range=None, ignore_walls=True, ignore_creatures=True, radius=None):
    """
    This menu lets the player select a tile on the map.
    The game pauses, produces a screen rectangle, and returns the map address when the LMB is clicked.
    :return: (x,y) map address tuple
    """

    menu_close = False
    while not menu_close:

        # get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        map_coordinates_x = int(mouse_x / constants.CELL_WIDTH)
        map_coordinates_y = int(mouse_y / constants.CELL_HEIGHT)

        if origin:
            list_of_tiles = map_find_line(origin, (map_coordinates_x, map_coordinates_y))
        else:
            list_of_tiles = [(map_coordinates_x, map_coordinates_y)]

        if max_range:
            list_of_tiles = list_of_tiles[:max_range + 1]

        for i, (x, y) in enumerate(list_of_tiles):
            if i == 0:
                continue
            if not ignore_walls and map_check_for_wall(x, y):
                list_of_tiles = list_of_tiles[:i + 1]
                break
            if not ignore_creatures and map_check_for_creature(x, y):
                list_of_tiles = list_of_tiles[:i + 1]
                break

        # get button clicks
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    menu_close = True
                if event.key == pygame.K_ESCAPE:
                    menu_close = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return list_of_tiles[-1]

        # draw game first
        draw_game()

        # draw rectangle at mouse position on top of game
        if len(list_of_tiles) > 1:
            for tile in list_of_tiles[1:]:
                draw_tile_rect(tile)

        if radius:
            area_of_effect = map_find_radius(list_of_tiles[-1], radius)
            for x, y in area_of_effect:
                draw_tile_rect((x, y), tile_color=constants.COLOR_RED)

        else:
            draw_tile_rect((map_coordinates_x, map_coordinates_y))

        pygame.display.flip()
        CLOCK.tick(constants.GAME_FPS)


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

        # update the display
        pygame.display.flip()

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
    pygame.key.set_repeat(200, 70)

    SURFACE_MAIN = pygame.display.set_mode((
            constants.MAP_WIDTH * constants.CELL_WIDTH,
            constants.MAP_HEIGHT * constants.CELL_HEIGHT
        ))

    GAME = ObjectGame()

    CLOCK = pygame.time.Clock()

    FOV_CALCULATE = True
    
    ASSETS = StructureAssets()

    container_com1 = ComponentContainer()
    creature_comp1 = ComponentCreature('Greg')
    PLAYER = ObjActor(1, 1, 'Python', ASSETS.A_PLAYER, animation_speed=1, creature=creature_comp1, container=container_com1)

    item_com1 = ComponentItem(use_function=cast_heal, value=5)
    creature_comp2 = ComponentCreature('Jack', death_function=death_monster)
    ai_com = AITest()
    ENEMY = ObjActor(15, 15, 'Lobster', ASSETS.A_ENEMY, animation_speed=1, creature=creature_comp2, ai=ai_com, item=item_com1)

    item_com2 = ComponentItem(use_function=cast_heal, value=5)
    creature_comp3 = ComponentCreature('Bob', death_function=death_monster)
    ai_com2 = AITest()
    ENEMY2 = ObjActor(14, 15, 'Faux Crab', ASSETS.A_ENEMY, animation_speed=1, creature=creature_comp3, ai=ai_com2, item=item_com2)

    GAME.current_objects = [PLAYER, ENEMY, ENEMY2]


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
            if event.key == pygame.K_p:
                menu_pause()
            if event.key == pygame.K_i:
                menu_inventory()
            if event.key == pygame.K_l:
                cast_fireball()

    return 'no-action'


def game_message(message, color=constants.COLOR_GREY):
    GAME.message_history.append((message, color))


#############################################################
###################################################   #######
###############################################   /~\   #####
############################################   _- `~~~', ####
##########################################  _-~       )  ####
#######################################  _-~          |  ####
####################################  _-~            ;  #####
##########################  __---___-~              |   #####
#######################   _~   ,,                  ;  `,,  ##
#####################  _-~    ;'                  |  ,'  ; ##
###################  _~      '                    `~'   ; ###
############   __---;                                 ,' ####
########   __~~  ___                                ,' ######
#####  _-~~   -~~ _                               ,' ########
##### `-_         _                              ; ##########
#######  ~~----~~~   ;                          ; ###########
#########  /          ;                        ; ############
#######  /             ;                      ; #############
#####  /                `                    ; ##############
###  /                                      ; ###############
#                                            ################

if __name__ == '__main__':
    game_initialize()
    game_main_loop()
