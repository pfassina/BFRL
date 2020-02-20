# modules
from datetime import date
import math
import pygame

# game files
from bfrl import constants
from bfrl import game
from bfrl import globals
from bfrl import draw


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
    def __init__(self, x, y, name_object, animation_key, animation_speed=0.5, depth=0, state=None,
                 creature=None, ai=None, container=None, item=None, equipment=None, stairs=None,
                 exit_portal=None):
        """
        :param x: starting x position on the current map
        :param y: starting y position on the current map
        :param name_object: string containing the name of the object, "chair" or "goblin" for example.
        :param animation_key: A list of images that make up the object's sprite sheet.
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
        self.animation = globals.ASSETS.sprite(self.animation_key)

        self.animation_speed = animation_speed / 1.0

        # animation flicker speed
        self.flicker_speed = self.animation_speed / len(self.animation)
        self.flicker_timer = 0.0
        self.sprite_image = 0

        # Draw depth relative to surface
        self.depth = depth

        self.state = state

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

        self.exit_portal = exit_portal
        if self.exit_portal:
            self.exit_portal.owner = self

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
        is_visible = globals.FOV_MAP.fov[self.y, self.x]
        x_cell = self.x * constants.CELL_WIDTH
        y_cell = self.y * constants.CELL_HEIGHT

        if is_visible:
            if len(self.animation) == 1:
                globals.SURFACE_MAP.blit(self.animation[0], (x_cell, y_cell))
            elif len(self.animation) > 1:
                if globals.CLOCK.get_fps() > 0.0:
                    self.flicker_timer += 1 / globals.CLOCK.get_fps()
                if self.flicker_timer >= self.flicker_speed:
                    self.flicker_timer = 0.0
                    if self.sprite_image >= len(self.animation) - 1:
                        self.sprite_image = 0
                    else:
                        self.sprite_image += 1
                draw_location = (x_cell, y_cell)
                globals.SURFACE_MAP.blit(self.animation[self.sprite_image], draw_location)

    def animation_destroy(self):
        self.animation = None

    def animation_initialize(self):
        self.animation = globals.ASSETS.sprite(self.animation_key)

    def set_position(self, coordinates):
        self.x, self.y = coordinates

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

        tile_is_wall = (globals.GAME.current_map.map_tiles[self.owner.x + dx][self.owner.y + dy].block_path is True)

        target = globals.GAME.current_map.check_for_creature(self.owner.x + dx, self.owner.y + dy, self.owner)
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
        damage_dealt = max(self.power - target.creature.defense, 0)
        message = f'{self.name_instance} attacks {target.creature.name_instance} for {damage_dealt} damage!'
        game.message(message, constants.COLOR_RED)
        target.creature.take_damage(damage_dealt)

        if damage_dealt > 0 and self.owner is globals.PLAYER:
            pygame.mixer.Sound.play(globals.RANDOM_ENGINE.choice(globals.ASSETS.sound_hit_list))

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
        message = f"{self.owner.display_name}'s health is {self.hp}/{self.max_hp}"
        game.message(message, constants.COLOR_WHITE)

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
                game.message('Not enough room to pick up', color=constants.COLOR_RED)
            else:
                game.message('Picking up')
                # add item to actor inventory
                actor.container.inventory.append(self.owner)
                # remove animation for game save
                self.owner.animation = None

                # remove item from globals.GAME
                globals.GAME.objects_on_map.remove(self.owner)

                # assigns container ownership to actor's container
                self.container = actor.container

    def drop(self, new_x, new_y):

        # add item to game objects
        globals.GAME.objects_on_map.append(self.owner)

        # load item animation
        self.owner.animation = globals.ASSETS.sprite(self.owner.animation_key)

        # remove item from actor container
        self.container.inventory.remove(self.owner)

        # drop item at actor position
        self.owner.x = new_x
        self.owner.y = new_y

        game.message('Item dropped!')

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
                game.message('equipment slot is occupied', constants.COLOR_RED)
                return

        # equips if slot is free
        self.equipped = True
        game.message('Item equipped')

    def unequip(self):
        self.equipped = False
        game.message('Item unequipped')


class ComponentStairs:

    def __init__(self, downwards=True):
        self.downwards = downwards

    def use(self):
        if self.downwards:
            globals.GAME.transition_next()
        else:
            globals.GAME.transition_previous()


class ComponentExitPortal:

    def __init__(self):
        self.open_sprite = 'S_PORTAL_OPEN'
        self.closed_sprite = 'S_PORTAL_CLOSED'
        self.found_lamp = False

    def update(self):

        for obj in globals.PLAYER.container.inventory:
            if obj.name_object == 'The Lamp' and self.owner.state != 'OPEN':
                self.found_lamp = True
                self.owner.state = 'OPEN'
                self.owner.animation_key = self.open_sprite
                self.owner.animation = globals.ASSETS.sprite(self.open_sprite)

        if not self.found_lamp and self.owner.state == 'OPEN':
            self.owner.state = 'CLOSED'
            self.owner.animation_key = self.closed_sprite
            self.owner.animation = globals.ASSETS.sprite(self.closed_sprite)

    def use(self):

        if self.found_lamp:

            globals.PLAYER.state = 'STATUS WIN'
            globals.SURFACE_MAIN.fill(constants.COLOR_BLACK)
            win_text = {
                'display_surface': globals.SURFACE_MAIN,
                'text_to_display': 'YOU WON!',
                'font': constants.FONT_TITLE_SCREEN,
                'coordinates': (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2),
                'text_color': constants.COLOR_WHITE,
                'alignment': 'center',
            }
            draw.text(**win_text)

            filename = f"{globals.PLAYER.display_name}-{date.today().strftime('%Y%m%d')}.txt"
            with open(f'data/legacy/{filename}', 'a+') as legacy_file:
                for msg, _ in globals.GAME.message_history:
                    legacy_file.write(f'{msg}\n')

            milliseconds_passed = 0
            while milliseconds_passed <= 2000:
                pygame.event.get()
                milliseconds_passed += globals.CLOCK.tick(constants.GAME_FPS)
                pygame.display.update()
