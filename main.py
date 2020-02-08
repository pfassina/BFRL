# modules
import gzip
import math
import numpy as np
import pickle
import pygame
import tcod

# game files
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
        self.ss_player = ObjectSpriteSheet('data/reptiles.png')
        self.ss_enemy = ObjectSpriteSheet('data/reptiles.png')
        self.ss_items = ObjectSpriteSheet('data/scroll.png')
        self.ss_flesh = ObjectSpriteSheet('data/flesh.png')
        self.ss_tile = ObjectSpriteSheet('data/tile.png')

        # Animations
        self.A_PLAYER = self.ss_player.get_animation('m', 5, width=16, height=16, num_sprites=2, scale=(32, 32))
        self.A_SNAKE_01 = self.ss_enemy.get_animation('e', 5, width=16, height=16, num_sprites=2, scale=(32, 32))
        self.A_SNAKE_02 = self.ss_enemy.get_animation('k', 5, width=16, height=16, num_sprites=2, scale=(32, 32))
        self.A_MOUSE_01 = self.ss_enemy.get_animation('g', 11, width=16, height=16, num_sprites=2, scale=(32, 32))

        # Tiles
        self.S_WALL = pygame.image.load('data/wall.jpg')
        self.S_WALL_EXPLORED = pygame.image.load('data/wall_explored.png')

        self.S_FLOOR = pygame.image.load('data/floor.png')
        self.S_FLOOR_EXPLORED = pygame.image.load('data/floor_explored.png')

        self.S_STAIRS_UP = self.ss_tile.get_animation('d', 3, width=16, height=16, num_sprites=1, scale=(32, 32))
        self.S_STAIRS_DOWN = self.ss_tile.get_animation('f', 3, width=16, height=16, num_sprites=1, scale=(32, 32))

        # Items
        sword_img = pygame.image.load('data/sword.png')
        self.S_SWORD = [pygame.transform.scale(sword_img, (constants.CELL_WIDTH, constants.CELL_HEIGHT))]

        shield_img = pygame.image.load('data/shield.png')
        self.S_SHIELD = [pygame.transform.scale(shield_img, (constants.CELL_WIDTH, constants.CELL_HEIGHT))]

        self.S_SCROLL_01 = self.ss_items.get_animation('d', 0, width=16, height=16, num_sprites=1, scale=(32, 32))
        self.S_SCROLL_02 = self.ss_items.get_animation('b', 1, width=16, height=16, num_sprites=1, scale=(32, 32))
        self.S_SCROLL_03 = self.ss_items.get_animation('c', 5, width=16, height=16, num_sprites=1, scale=(32, 32))

        self.S_FLESH_01 = self.ss_flesh.get_animation('a', 3, width=16, height=16, num_sprites=1, scale=(32, 32))
        self.S_FLESH_02 = self.ss_flesh.get_animation('c', 0, width=16, height=16, num_sprites=1, scale=(32, 32))

    def sprite(self, key):
        animation_dict = {
            # creatures
            'A_PLAYER': self.A_PLAYER,
            'A_SNAKE_01': self.A_SNAKE_01,
            'A_SNAKE_02': self.A_SNAKE_02,
            'A_MOUSE_01': self.A_MOUSE_01,

            # tiles
            'S_WALL': self.S_WALL,
            'S_WALL_EXPLORED': self.S_WALL_EXPLORED,
            'S_FLOOR': self.S_FLOOR,
            'S_FLOOR_EXPLORED': self.S_FLOOR_EXPLORED,
            'S_STAIRS_UP': self.S_STAIRS_UP,
            'S_STAIRS_DOWN': self.S_STAIRS_DOWN,

            # items
            'S_SWORD': self.S_SWORD,
            'S_SHIELD': self.S_SHIELD,
            'S_SCROLL_01': self.S_SCROLL_01,
            'S_SCROLL_02': self.S_SCROLL_02,
            'S_SCROLL_03': self.S_SCROLL_03,
            'S_FLESH_01': self.S_FLESH_01,
            'S_FLESH_02': self.S_FLESH_02,
        }
        return animation_dict[key]


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
    def __init__(self, x, y, name_object, animation_key, animation_speed=0.5,
                 creature=None, ai=None, container=None, item=None, equipment=None, stairs=None):
        """
        :param x: starting x position on the current map
        :param y: starting y position on the current map
        :param name_object: string containing the name of the object, "chair" or "goblin" for example.
        :param animation_key: A list of images that make up the object's sprite sheet. Created with StructureAssets class.
        :param animation_speed: Time in seconds it takes to loop through the object animation.
        :param creature: any object that has health, and generally can fight
        :param ai: ai is a component that executes an action every time the object is able to act
        :param container: containers are objects that can hold an inventory
        :param item: items are items that are able to be picked up and used
        """

        self.x = x
        self.y = y

        self.name_object = name_object

        self.animation_key = animation_key
        self.animation = ASSETS.sprite(self.animation_key)

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

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self

            # adds an item component to the equipment'owner
            self.item = ComponentItem()
            self.item.owner = self

        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self


    @property
    def display_name(self):
        """Returns the best name to display for this object"""
        if self.creature:
            return f'{self.creature.name_instance} the {self.name_object}'
        if self.item:
            if self.equipment and self.equipment.equipped:
                return f'{self.name_object} (EQP)'
            else:
                return self.name_object

    def draw(self):
        """draws the obj_Actor to the screen"""
        is_visible = FOV_MAP.fov[self.y, self.x]
        if is_visible:
            if len(self.animation) == 1:
                SURFACE_MAP.blit(self.animation[0], (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT))
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
                SURFACE_MAP.blit(self.animation[self.sprite_image], draw_location)

    def distance_to(self, other):

        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx ** 2 + dy ** 2)

    def move_towards(self, other):

        dx = other.x - self.x
        dy = other.y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance, 0))
        dy = int(round(dy / distance, 0))

        self.creature.move(dx, dy)

    def move_away(self, other):

        dx = self.x - other.x
        dy = self.y - other.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance, 0))
        dy = int(round(dy / distance, 0))

        self.creature.move(dx, dy)


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

        self.current_objects = []
        self.message_history = []
        self.maps_previous = []
        self.maps_next = []
        self.current_map, self.current_rooms = map_create()

    def transition_next(self):

        global FOV_CALCULATE

        # destroy surfaces to allow game save
        for obj in self.current_objects:
            obj.animation = None

        # save current map to previous maps
        self.maps_previous.append((PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects))

        if len(self.maps_next) == 0:

            # clear current_objects list
            self.current_objects = [PLAYER]

            # add Sprite back to Player
            PLAYER.animation = ASSETS.sprite(PLAYER.animation_key)

            # create new map and place objects
            self.current_map, self.current_rooms = map_create()
            map_place_objects(self.current_rooms)

        else:
            # load next map
            PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects = self.maps_next.pop(-1)

            # load destroyed surfaces
            for obj in self.current_objects:
                obj.animation = ASSETS.sprite(obj.animation_key)

            # calculate FOV
            map_make_fov(self.current_map)
        FOV_CALCULATE = True

    def transition_previous(self):

        global FOV_CALCULATE

        if len(self.maps_previous) > 0:

            # destroy surfaces to allow game save
            for obj in self.current_objects:
                obj.animation = None

            # save current map to next maps
            self.maps_next.append((PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects))

            # load last map
            PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects = self.maps_previous.pop(-1)

            # load destroyed surfaces on previous map
            for obj in self.current_objects:
                obj.animation = ASSETS.sprite(obj.animation_key)

            # calculate fov
            map_make_fov(self.current_map)
            FOV_CALCULATE = True


class ObjectCamera:

    def __init__(self):

        self.width = constants.CAMERA_WIDTH
        self.height = constants.CAMERA_HEIGHT
        self.x, self.y = (0, 0)

    @property
    def rectangle(self):
        camera_rectangle = pygame.Rect((0, 0), (self.width, self.height))
        camera_rectangle.center = (self.x, self.y)
        return camera_rectangle

    @property
    def map_address(self):
        map_x = int(self.x / constants.CELL_WIDTH)
        map_y = int(self.y / constants.CELL_HEIGHT)

        return map_x, map_y

    def update(self):

        target_x = PLAYER.x * constants.CELL_WIDTH + constants.CELL_WIDTH / 2
        target_y = PLAYER.y * constants.CELL_HEIGHT + constants.CELL_HEIGHT / 2

        distance_x, distance_y = self.map_distance((target_x, target_y))

        self.x += int(distance_x * .1)
        self.y += int(distance_y * .1)

    def window_to_map(self, coordinates):

        # convert coordinates to distance from camera
        x_distance, y_distance = self.camera_distance(coordinates)

        # convert distance from camera to a map pixel coordinate
        map_x = self.x + x_distance
        map_y = self.y + y_distance

        return map_x, map_y

    def camera_distance(self, coordinates):

        window_x, window_y = coordinates
        distance_x = window_x - self.width / 2
        distance_y = window_y - self.height / 2

        return distance_x, distance_y

    def map_distance(self, coordinates):

        map_x, map_y = coordinates

        dist_x = map_x - self.x
        dist_y = map_y - self.y

        return dist_x, dist_y


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

    def get_animation(self, column, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, num_sprites=1,
                      scale=None):
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


class ObjectRoom:
    """
    This is a rectangle room that lives on the map.
    """

    def __init__(self, coordinates, size):

        self.x1, self.y1 = coordinates
        self.w, self.h = size
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

    @property
    def center(self):
        center_x = int((self.x1 + self.x2)/2)
        center_y = int((self.y1 + self.y2)/2)
        return center_x, center_y

    def intercept(self, other):

        x_overlap = self.x1 <= other.x2 and self.x2 >= other.x1
        y_overlap = self.y1 <= other.y2 and self.y2 >= other.y1
        return x_overlap and y_overlap


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
    ComponentCreature.move : allows the creature to move to a different tile
    ComponentCreature.attack : allows the creature to attack a target.
    ComponentCreature.take_damage : Creature takes damage. If health falls below 0, executes the death function.
    """

    def __init__(self, name_instance, base_attack=2, base_defense=0, hp=10, death_function=None):
        """
        :param name_instance: String, name of specific object. "Bob" for example.
        :param hp: integer, health of the creature. Is converted into both the maximum health and the current health.
        :param death_function: function that is executed whenever the creature's health dips below 0.
        """
        self.name_instance = name_instance
        self.base_attack = base_attack
        self.base_defense = base_defense
        self.hp = hp
        self.max_hp = hp
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
            self.attack(target)

        if not tile_is_wall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target):
        """
        Allows the creature to attack a target
        :param target: object attacked by the creature
        """
        damage_dealt = self.power - target.creature.defense
        message = f'{self.name_instance} attacks {target.creature.name_instance} for {damage_dealt} damage!'
        game_message(message, constants.COLOR_RED)
        target.creature.take_damage(damage_dealt)

    @property
    def power(self):
        """
        return creature's total power
        :return: total power
        """

        total_power = self.base_attack
        if self.owner.container:
            object_bonuses = [obj.equipment.attack_bonus for obj in self.owner.container.equipped_items]
            for bonus in object_bonuses:
                total_power += bonus

        return total_power

    @property
    def defense(self):
        """
        returns creature's total defense
        :return: total defense
        """

        total_defense = self.base_defense
        if self.owner.container:
            object_bonuses = [obj.equipment.defense_bonus for obj in self.owner.container.equipped_items]
            for bonus in object_bonuses:
                total_defense += bonus

        return total_defense

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

    @property
    def equipped_items(self):
        """
        returns a list of all items that are currently equipped.
        :return: list of equipped items
        """

        list_of_equipped_items = [obj for obj in self.inventory if obj.equipment and obj.equipment.equipped]
        return list_of_equipped_items

    # get the weight of everything within container


class ComponentItem:
    def __init__(self, weight=0.0, volume=0.0, use_function=None, value=None):
        self.weight = weight
        self.volume = volume
        self.use_function = use_function
        self.value = value
        self.container = None

    def pick_up(self, actor):

        # check if actor container can hold the item
        if actor.container:
            if actor.container.volume + self.volume > actor.container.max_volume:
                game_message('Not enough room to pick up', color=constants.COLOR_RED)
            else:
                game_message('Picking up')
                # add item to actor inventory
                actor.container.inventory.append(self.owner)
                # remove animation for game save
                self.owner.animation = None

                # remove item from game
                GAME.current_objects.remove(self.owner)

                # assigns container ownership to actor's container
                self.container = actor.container

    def drop(self, new_x, new_y):

        # add item to game objects
        GAME.current_objects.append(self.owner)

        # load item animation
        self.owner.animation = ASSETS.sprite(self.owner.animation_key)

        # remove item from actor container
        self.container.inventory.remove(self.owner)

        # drop item at actor position
        self.owner.x = new_x
        self.owner.y = new_y

        game_message('Item dropped!')

    def use(self):
        # Use the item by production an effect and removing it

        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        if self.use_function:
            result = self.use_function(self.container.owner, self.value)
            if result is not None:
                print('use_function_failed')
            else:
                self.container.inventory.remove(self.owner)


class ComponentEquipment:

    def __init__(self, attack_bonus=0, defense_bonus=0, slot=None):

        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.slot = slot

        self.equipped = False

    def toggle_equip(self):
        if self.equipped:
            self.unequip()
        else:
            self.equip()

    def equip(self):

        # check for equipment in slot
        all_equipped_items = self.owner.item.container.equipped_items

        for item in all_equipped_items:
            if item.equipment.slot == self.slot:
                game_message('equipment slot is occupied', constants.COLOR_RED)
                return

        # equips if slot is free
        self.equipped = True
        game_message('Item equipped')

    def unequip(self):
        self.equipped = False
        game_message('Item unequipped')


class ComponentStairs:

    def __init__(self, downwards=True):
        self.downwards = downwards

    def use(self):
        if self.downwards:
            GAME.transition_next()
        else:
            GAME.transition_previous()


#      ___       __
#     /   \     |  |
#    /  ^  \    |  |
#   /  /_\  \   |  |
#  /  _____  \  |  |
# /__/     \__\ |__|


class AIConfuse:
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
            game_message(f'{self.owner.display_name} has broken free!', constants.COLOR_RED)


class AIChase:
    """
    Basic monster AI which chases and tries to harm the player
    """

    def take_turn(self):

        monster = self.owner
        if FOV_MAP.fov[monster.y, monster.x]:
            # Moves towards the player if far away
            if monster.distance_to(PLAYER) >= 2:
                monster.move_towards(PLAYER)
            # If close enough, attack player
            elif PLAYER.creature.hp > 0:
                monster.creature.attack(PLAYER)


class AIFlee:
    """
    Basic monster AI which flees from the player
    """

    def take_turn(self):
        monster = self.owner
        if FOV_MAP.fov[monster.y, monster.x]:
            monster.move_away(PLAYER)

#  _______   _______     ___   .___________. __    __
# |       \ |   ____|   /   \  |           ||  |  |  |
# |  .--.  ||  |__     /  ^  \ `---|  |----`|  |__|  |
# |  |  |  ||   __|   /  /_\  \    |  |     |   __   |
# |  '--'  ||  |____ /  _____  \   |  |     |  |  |  |
# |_______/ |_______/__/     \__\  |__|     |__|  |__|
#


def death_monster(monster):
    """
    On death, most monsters stop moving.
    :param monster: Monster instance
    """

    message = f'{monster.creature.name_instance} is dead!'
    game_message(message, constants.COLOR_GREY)
    monster.animation_key = 'S_FLESH_01'
    monster.animation = ASSETS.sprite('S_FLESH_01')
    monster.creature = None
    monster.ai = None


def def_mouse(mouse):

    message = f'{mouse.creature.name_instance} is dead! A delicious corpse drops to the ground.'
    game_message(message, constants.COLOR_GREY)
    mouse.animation_key = 'S_FLESH_02'
    mouse.animation = ASSETS.sprite('S_FLESH_02')
    mouse.creature = None
    mouse.ai = None

# .___  ___.      ___      .______
# |   \/   |     /   \     |   _  \
# |  \  /  |    /  ^  \    |  |_)  |
# |  |\/|  |   /  /_\  \   |   ___/
# |  |  |  |  /  _____  \  |  |
# |__|  |__| /__/     \__\ | _|


def map_create():

    # Create a map of Height by Width dimensions
    new_map = [[StructureTile(True) for _ in range(0, constants.MAP_HEIGHT)] for _ in range(0, constants.MAP_WIDTH)]

    # Generate new room
    list_of_rooms = []
    for room in range(constants.MAP_MAX_NUM_ROOMS):

        w = tcod.random_get_int(None, constants.ROOM_MIN_WIDTH, constants.ROOM_MAX_WIDTH)
        h = tcod.random_get_int(None, constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT)

        x = tcod.random_get_int(None, 2, constants.MAP_WIDTH - w - 2)
        y = tcod.random_get_int(None, 2, constants.MAP_HEIGHT - h - 2)

        new_room = ObjectRoom((x, y), (w, h))

        # Check for interference
        failed = False
        for other_room in list_of_rooms:
            if new_room.intercept(other_room):
                failed = True

        # Place the room
        if not failed:
            map_create_room(new_map, new_room)

            if len(list_of_rooms) != 0:
                other_room = list_of_rooms[-1]
                map_create_tunnel(new_map, new_room.center, other_room.center)

            list_of_rooms.append(new_room)

    map_make_fov(new_map)

    return new_map, list_of_rooms


def map_create_room(new_map, room):
    for x in range(room.x1, room.x2):
        for y in range(room.y1, room.y2):
            new_map[x][y].block_path = False


def map_create_tunnel(new_map, room1, room2):

    x1, y1 = room1
    x2, y2 = room2

    if coin_flip:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y1].block_path = False
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[x2][y].block_path = False
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[y][x1].block_path = False
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y2].block_path = False


def map_place_objects(room_list):

    top_level = (len(GAME.maps_previous) == 0)
    rooms = len(room_list) - 1
    for index, room in enumerate(room_list):
        if index == 0:
            PLAYER.x, PLAYER.y = room.center
            if not top_level:
                gen_stairs(room.center, downwards=False)
            continue

        if index == rooms:
            gen_stairs(room.center)

        # Place a random enemy
        x = roll_dice(start=room.x1 + 1, sides=room.x2 - 1)
        y = roll_dice(start=room.y1 + 1, sides=room.y2 - 1)

        gen_enemy((x, y))

        # Place a random item
        x = roll_dice(start=room.x1 + 1, sides=room.x2 - 1)
        y = roll_dice(start=room.y1 + 1, sides=room.y2 - 1)
        gen_item((x, y))


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
    SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

    CAMERA.update()

    # draw the map
    draw_map(GAME.current_map)

    # draw the characters
    for obj in GAME.current_objects:
        obj.draw()

    SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)

    draw_debug()
    draw_messages()


def draw_map(map_to_draw):

    camera_x, camera_y = CAMERA.map_address
    display_map_width = constants.CAMERA_WIDTH / constants.CELL_WIDTH
    display_map_height = constants.CAMERA_HEIGHT / constants.CELL_HEIGHT

    # Define Dimensions of the map to be drawn
    render_width_min = int(camera_x - display_map_width / 2)
    render_width_min = max(render_width_min, 0)

    render_width_max = int(camera_x + display_map_width / 2)
    render_width_max = min(render_width_max, constants.MAP_WIDTH)

    render_height_min = int(camera_y - display_map_height / 2)
    render_height_min = max(render_height_min, 0)

    render_height_max = int(camera_y + display_map_height / 2)
    render_height_max = min(render_height_max, constants.MAP_HEIGHT)

    for x in range(render_width_min, render_width_max):
        for y in range(render_height_min, render_height_max):

            is_visible = FOV_MAP.fov[y, x]
            if is_visible:

                map_to_draw[x][y].explored = True
                if map_to_draw[x][y].block_path:
                    SURFACE_MAP.blit(ASSETS.S_WALL, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))
                else:
                    SURFACE_MAP.blit(ASSETS.S_FLOOR, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))

            elif map_to_draw[x][y].explored:
                if map_to_draw[x][y].block_path:
                    SURFACE_MAP.blit(ASSETS.S_WALL_EXPLORED, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))
                else:
                    SURFACE_MAP.blit(ASSETS.S_FLOOR_EXPLORED, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))


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

    start_y = constants.CAMERA_HEIGHT - (constants.NUM_MESSAGES * text_height) - 10

    for index, (message, color) in enumerate(to_draw):
        message_location = (0, start_y + index * text_height)
        draw_text(SURFACE_MAIN, message, constants.FONT_MESSAGE_TEXT, message_location, color, constants.COLOR_BLACK)


def draw_text(display_surface, text_to_display, font, coordinates, text_color, back_color=None, alignment='top-left'):

    """
    This function takes in some text, and display it on the referenced surfaced
    :param alignment:
    :param display_surface: Surface to display text
    :param text_to_display: Text to be displayed
    :param font: font of the text
    :param coordinates: Coordinates tuple
    :param text_color: Text color
    :param back_color: Text background color
    """

    text_surface, text_rectangle = helper_text_objects(text_to_display, font, text_color, back_color)

    if alignment == 'top-left':
        text_rectangle.topleft = coordinates
    elif alignment == 'center':
        text_rectangle.center = coordinates
    else:
        text_rectangle.topleft = coordinates

    display_surface.blit(text_surface, text_rectangle)


def draw_tile_rect(coordinates, tile_color=None, tile_alpha=150, marker=None):

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

    if marker:
        mx = int(round(constants.CELL_WIDTH / 2))
        my = int(round(constants.CELL_HEIGHT / 2))
        marker_font = constants.FONT_CURSOR_TEXT
        marker_color = constants.COLOR_BLACK
        align = 'center'
        draw_text(new_surface, marker, font=marker_font, coordinates=(mx, my), text_color=marker_color, alignment=align)

    # SURFACE_MAIN
    SURFACE_MAP.blit(new_surface, (new_x, new_y))


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


def cast_heal(caster, value):
    """
    Casts heals, increasing target HP by value amount. Cast cancelled if creature at Max HP.
    :param caster: Creature targeted by Heal
    :param value: Heal amount
    :return: None if successful, 'canceled' if not
    """

    if caster.creature.hp == caster.creature.max_hp:
        game_message(f'{caster.creature.name_instance} the {caster.name_object} already at max hp.')
        return 'canceled'
    else:
        caster.creature.heal(value)
        heal_value = min(value, caster.creature.max_hp - value)
        game_message(f'{caster.display_name}  healed for {heal_value} health.')
        return None


def cast_lightning(caster, value):

    spell_range, spell_range = value

    # prompt player for a tile
    origin_tile = (caster.x, caster.y)
    target_tile = menu_tile_select(origin_tile, max_range=spell_range, ignore_walls=False)

    # convert that tile into a list of tiles between player and target
    if target_tile:
        list_of_tiles = map_find_line(origin_tile, target_tile)

    # cycle through list, damage all creatures for value
        for x, y in list_of_tiles[1:]:
            target = map_check_for_creature(x, y)
            if target:
                game_message(f'{target.display_name} is hit by a lightning bolt and takes {spell_range} damage!')
                target.creature.take_damage(spell_range)
    else:
        print('cast lightning cancelled.')


def cast_fireball(caster, value):

    spell_damage, spell_radius, spell_range = value

    # Get target tile
    origin_tile = (caster.x, caster.y)
    target_tile = menu_tile_select(origin_tile, max_range=spell_range, ignore_walls=False, ignore_creatures=False,
                                   radius=spell_radius)

    # get sequence of tiles
    if target_tile:
        list_of_tiles = map_find_radius(target_tile, spell_radius)

        # damage all creatures in tiles
        for x, y in list_of_tiles:
            target = map_check_for_creature(x, y)
            if target:
                game_message(f'{target.display_name} is hit by a fireball and takes {spell_damage} damage!')
                target.creature.take_damage(spell_damage)
    else:
        print('cast lightning cancelled.')


def cast_confusion(_, effect_length):

    # get target
    target_tile = menu_tile_select()
    if target_tile:
        tx, ty = target_tile
        target = map_check_for_creature(tx, ty)

        # temporarily confuse the target
        if target:
            o_ai = target.ai
            target.ai = AIConfuse(old_ai=o_ai, num_turns=effect_length)
            target.ai.owner = target

            game_message(f"{target.display_name} is confused. The creature's eyes glaze over", constants.COLOR_GREEN)


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

    window_width = constants.CAMERA_WIDTH
    window_height = constants.CAMERA_HEIGHT

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

    window_width = constants.CAMERA_WIDTH
    window_height = constants.CAMERA_HEIGHT

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
        item_list = [item.display_name for item in PLAYER.container.inventory]

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
                    # TODO keep inventory open if item is an equipment
                    menu_close = True

        # Draw item list
        for line, name in enumerate(item_list):
            name_location = (0, 0 + line * menu_text_height)
            if line == mouse_line_selection and mouse_in_window:
                draw_text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_mouse_over_bg)
            else:
                draw_text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_bg_color)

        # Render Game

        draw_game()

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
        mouse_coordinates = pygame.mouse.get_pos()
        map_coordinate_x, map_coordinate_y = CAMERA.window_to_map(mouse_coordinates)

        map_address_x = int(map_coordinate_x / constants.CELL_WIDTH)
        map_address_y = int(map_coordinate_y / constants.CELL_HEIGHT)

        if origin:
            list_of_tiles = map_find_line(origin, (map_address_x, map_address_y))
        else:
            list_of_tiles = [(map_address_x, map_address_y)]

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
        SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
        SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

        CAMERA.update()

        # draw the map first
        draw_map(GAME.current_map)
        for obj in GAME.current_objects:
            obj.draw()

        # draw rectangle at mouse position on top of game
        if len(list_of_tiles) > 1:
            for tile in list_of_tiles[1:]:
                if tile == list_of_tiles[-1]:
                    draw_tile_rect(tile, marker='X')
                else:
                    draw_tile_rect(tile)

            # TODO: Show radius if len = 1
            if radius:
                area_of_effect = map_find_radius(list_of_tiles[-1], radius)
                for x, y in area_of_effect:
                    draw_tile_rect((x, y), tile_color=constants.COLOR_RED)

        else:
            draw_tile_rect((map_address_x, map_address_y), marker='X')

        # update main surface with the new map
        SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)

        draw_debug()
        draw_messages()

        pygame.display.flip()
        CLOCK.tick(constants.GAME_FPS)


#  _______   ______   .______     .___________. __    __  .__   __.  _______
# |   ____| /  __  \  |   _  \    |           ||  |  |  | |  \ |  | |   ____|
# |  |__   |  |  |  | |  |_)  |   `---|  |----`|  |  |  | |   \|  | |  |__
# |   __|  |  |  |  | |      /        |  |     |  |  |  | |  . `  | |   __|
# |  |     |  `--'  | |  |\  \----.   |  |     |  `--'  | |  |\   | |  |____
# |__|      \______/  | _| `._____|   |__|      \______/  |__| \__| |_______|
#

@property
def coin_flip(): return np.random.choice([True, False])


def roll_dice(sides, rolls=None, start=1): return np.random.choice(range(start, sides), size=rolls)


#   _______  _______ .__   __.  _______ .______          ___   .___________.  ______   .______          _______.
#  /  _____||   ____||  \ |  | |   ____||   _  \        /   \  |           | /  __  \  |   _  \        /       |
# |  |  __  |  |__   |   \|  | |  |__   |  |_)  |      /  ^  \ `---|  |----`|  |  |  | |  |_)  |      |   (----`
# |  | |_ | |   __|  |  . `  | |   __|  |      /      /  /_\  \    |  |     |  |  |  | |      /        \   \
# |  |__| | |  |____ |  |\   | |  |____ |  |\  \----./  _____  \   |  |     |  `--'  | |  |\  \----.----)   |
#  \______| |_______||__| \__| |_______|| _| `._____/__/     \__\  |__|      \______/  | _| `._____|_______/
#


def gen_player(coordinates):

    global PLAYER

    x, y = coordinates

    bag = ComponentContainer()
    creature_component = ComponentCreature('Greg', base_attack=4)

    PLAYER = ObjActor(x, y, 'Python', 'A_PLAYER', animation_speed=1, creature=creature_component, container=bag)
    GAME.current_objects.append(PLAYER)

    return PLAYER


def gen_stairs(coordinates, downwards=True):

    x, y = coordinates
    if downwards:
        stairs_component = ComponentStairs()
        stairs = ObjActor(x, y, 'stairs down', animation_key='S_STAIRS_DOWN', stairs=stairs_component)
    else:
        stairs_component = ComponentStairs(downwards)
        stairs = ObjActor(x, y, 'stairs up', animation_key='S_STAIRS_UP', stairs=stairs_component)

    GAME.current_objects.append(stairs)


# Items
def gen_item(coordinates):

    generator_dict = {
        0: gen_scroll_lightning(coordinates),
        1: gen_scroll_fireball(coordinates),
        2: gen_scroll_confusion(coordinates),
        3: gen_weapon_sword(coordinates),
        4: gen_armor_shield(coordinates),
    }

    # generate random item with equal probability
    random_num = np.random.randint(0, len(generator_dict))

    item = generator_dict[random_num]
    GAME.current_objects.append(item)


def gen_scroll_lightning(coordinates):

    x, y = coordinates

    spell_damage = tcod.random_get_int(None, 5, 7)
    spell_range = tcod.random_get_int(None, 7, 8)

    item_component = ComponentItem(use_function=cast_lightning, value=(spell_damage, spell_range))
    scroll = ObjActor(x, y, "Lightning scroll", 'S_SCROLL_01', item=item_component)

    return scroll


def gen_scroll_fireball(coordinates):

    x, y = coordinates

    spell_damage = tcod.random_get_int(None, 2, 4)
    spell_radius = 1
    spell_range = tcod.random_get_int(None, 9, 12)

    item_component = ComponentItem(use_function=cast_fireball, value=(spell_damage, spell_radius, spell_range))
    scroll = ObjActor(x, y, "Fireball scroll", 'S_SCROLL_02', item=item_component)

    return scroll


def gen_scroll_confusion(coordinates):

    x, y = coordinates

    effect_length = tcod.random_get_int(None, 5, 10)

    item_component = ComponentItem(use_function=cast_confusion, value=effect_length)
    scroll = ObjActor(x, y, "Confusion scroll", 'S_SCROLL_03', item=item_component)

    return scroll


def gen_weapon_sword(coordinates):

    x, y = coordinates

    bonus = tcod.random_get_int(None, 1, 2)

    equipment_component = ComponentEquipment(attack_bonus=bonus, slot='hand_right')
    sword = ObjActor(x, y, "sword", 'S_SWORD', equipment=equipment_component)

    return sword


def gen_armor_shield(coordinates):

    x, y = coordinates

    bonus = tcod.random_get_int(None, 1, 2)

    equipment_component = ComponentEquipment(defense_bonus=bonus, slot='hand_left')
    shield = ObjActor(x, y, "shield", 'S_SHIELD', equipment=equipment_component)

    return shield


# Enemies
def gen_enemy(coordinates):

    generator_dict = {
        0: gen_snake_anaconda(coordinates),
        1: gen_snake_cobra(coordinates),
        2: gen_mouse(coordinates),
    }

    # Generate Random Snake based on p probability weights
    random_num = np.random.choice(len(generator_dict), p=[0.5, 0.15, 0.35])

    enemy = generator_dict[random_num]
    GAME.current_objects.append(enemy)


def gen_snake_anaconda(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic female'),
        'base_attack': tcod.random_get_int(None, 1, 2),
        'hp': tcod.random_get_int(None, 5, 10),
        'death_function': death_monster
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'anaconda',
        'animation_key': 'A_SNAKE_01',
        'animation_speed': 1,
        'creature': ComponentCreature(**creature_attributes),
        'ai': AIChase(),
    }

    anaconda = ObjActor(**actor_attributes)

    return anaconda


def gen_snake_cobra(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic male'),
        'base_attack': tcod.random_get_int(None, 3, 6),
        'hp': tcod.random_get_int(None, 15, 20),
        'death_function': death_monster
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'cobra',
        'animation_key': 'A_SNAKE_02',
        'animation_speed': 1,
        'creature': ComponentCreature(**creature_attributes),
        'ai': AIChase(),
    }

    cobra = ObjActor(**actor_attributes)

    return cobra


def gen_mouse(coordinates):

    x, y = coordinates

    creature_attributes = {
        'name_instance': tcod.namegen_generate('Celtic male'),
        'base_attack': 0,
        'hp': 1,
        'death_function': def_mouse
    }

    actor_attributes = {
        'x': x,
        'y': y,
        'name_object': 'mouse',
        'animation_key': 'A_MOUSE_01',
        'animation_speed': 1,
        'creature': ComponentCreature(**creature_attributes),
        'ai': AIFlee(),
        'item': ComponentItem(use_function=cast_heal, value=5),
    }

    cobra = ObjActor(**actor_attributes)

    return cobra


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
            game_exit()

        elif player_action != 'no-action':
            for obj in GAME.current_objects:
                if obj.ai:
                    obj.ai.take_turn()

        # draw the game
        draw_game()

        # update the display
        pygame.display.flip()

        CLOCK.tick(constants.GAME_FPS)


def game_initialize():
    """
    Initializes the main window and pygame
    """

    global SURFACE_MAIN, SURFACE_MAP, CLOCK, FOV_CALCULATE, PLAYER, ASSETS, CAMERA

    # initialize pygame
    pygame.init()
    pygame.key.set_repeat(200, 70)
    tcod.namegen_parse('data/celtic.cfg')

    # create display surface with a given Height, and Width
    SURFACE_MAIN = pygame.display.set_mode((constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT))

    SURFACE_MAP = pygame.Surface((
            constants.MAP_WIDTH * constants.CELL_WIDTH,
            constants.MAP_HEIGHT * constants.CELL_HEIGHT
        ))

    # CAMERA tracks what is shown on the display
    CAMERA = ObjectCamera()

    # ASSETS stores the game assets
    ASSETS = StructureAssets()

    # CLOCK tracks and limits CPU cycles
    CLOCK = pygame.time.Clock()

    # When FOV is true, FOV recalculates
    FOV_CALCULATE = True

    # Create a new game
    try:
        game_load()
    except FileNotFoundError:
        game_new()


def game_message(message, color=constants.COLOR_GREY):
    GAME.message_history.append((message, color))


def game_handle_keys():
    """
    Handles player inputs
    """
    global FOV_CALCULATE

    # get player input
    keys_list = pygame.key.get_pressed()
    events = pygame.event.get()

    # Check for mod key
    MOD_KEY = keys_list[pygame.K_RSHIFT] or keys_list[pygame.K_LSHIFT]

    for event in events:
        # Quit game if player closes window
        if event.type == pygame.QUIT:
            return 'QUIT'
        if event.type == pygame.KEYDOWN:
            # moves up by pressing the "Up" key
            if event.key == pygame.K_UP:
                PLAYER.creature.move(0, -1)
                FOV_CALCULATE = True
                return 'player-moved'
            # moves down by pressing the "Down" key
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                FOV_CALCULATE = True
                return 'player-moved'
            # moves left by pressing the "Left" key
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                FOV_CALCULATE = True
                return 'player-moved'
            # moves right by pressing the "Right" key
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                FOV_CALCULATE = True
                return 'player-moved'
            # Gets item from the ground by pressing the "g" key
            if event.key == pygame.K_g:
                objects_at_player = map_objects_at_coordinates(PLAYER.x, PLAYER.y)
                for obj in objects_at_player:
                    if obj.item:
                        obj.item.pick_up(PLAYER)
            # Drops first item in the inventory onto the ground by pressing the "d" key
            if event.key == pygame.K_d:
                if len(PLAYER.container.inventory) > 0:
                    PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
            # Pauses the game by pressing the "p" key
            if event.key == pygame.K_p:
                menu_pause()
            # Opens the inventory menu by pressing the "i" key
            if event.key == pygame.K_i:
                menu_inventory()
            # Open look menu by pressing the "l" key
            if event.key == pygame.K_l:
                menu_tile_select()
            # Go down or up stairs by pressing "SHIT + ."
            if MOD_KEY and event.key == pygame.K_PERIOD:
                objects_at_player = map_objects_at_coordinates(PLAYER.x, PLAYER.y)
                for obj in objects_at_player:
                    if obj.stairs:
                        obj.stairs.use()


    return 'no-action'


def game_new():

    global GAME

    # Creates new GAME
    GAME = ObjectGame()

    # Creates a player
    gen_player((0, 0))

    # Place objects on map
    map_place_objects(GAME.current_rooms)


def game_save():

    for obj in GAME.current_objects:
        obj.animation = None

    with gzip.open('savegame/savegame', 'wb') as file:
        pickle.dump([GAME, PLAYER], file)


def game_load():

    global GAME, PLAYER

    with gzip.open('savegame/savegame', 'rb') as file:
        GAME, PLAYER = pickle.load(file)

    for obj in GAME.current_objects:
        obj.animation = ASSETS.sprite(obj.animation_key)

    # make FOV
    map_make_fov(GAME.current_map)


def game_exit():

    game_save()
    pygame.quit()
    exit()


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
