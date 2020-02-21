# modules
import gzip
import os
import pickle
import pygame
import sys

# game files
from bfrl import constants
from bfrl import globals
from bfrl import maps
from bfrl import draw
from bfrl import menu
from bfrl import generator


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

        self.current_map = None
        self.message_history = []
        self.maps_previous = []
        self.maps_next = []

    def transition_next(self):

        # destroy surfaces to allow game save
        for obj in self.objects_on_map:
            obj.animation_destroy()

        # save current map to previous maps
        self.maps_previous.append((globals.PLAYER.x, globals.PLAYER.y, self.current_map, self.objects_on_map))

        if len(self.maps_next) == 0:

            # create new map object and place objects
            self.current_map = maps.GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT)

            # clear current_objects list
            self.current_map.list_of_objects = [globals.PLAYER]

            # initialize player animation
            globals.PLAYER.animation_initialize()

            # Generate dungeon
            self.current_map.generate_dungeon(
                constants.MAP_MAX_NUM_ROOMS,
                constants.ROOM_MIN_WIDTH, constants.ROOM_MAX_WIDTH,
                constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT
            )

        else:
            # load next map
            globals.PLAYER.x, globals.PLAYER.y, self.current_map, objects_on_map = self.maps_next.pop(-1)
            self.current_map.list_of_objects = objects_on_map

            # load destroyed surfaces
            for obj in self.objects_on_map:
                obj.animation_initialize()

            # calculate FOV
            maps.make_fov(self.current_map.map_tiles)

        globals.FOV_CALCULATE = True

    def transition_previous(self):

        if len(self.maps_previous) > 0:

            # destroy surfaces to allow game save
            for obj in self.objects_on_map:
                obj.animation = None

            # save current map to next maps
            self.maps_next.append((globals.PLAYER.x, globals.PLAYER.y, self.current_map, self.objects_on_map))

            # load last map
            globals.PLAYER.x, globals.PLAYER.y, self.current_map, objects = self.maps_previous.pop(-1)
            self.current_map.list_of_objects = objects

            # load destroyed surfaces on previous map
            for obj in self.objects_on_map:
                obj.animation = globals.ASSETS.sprite(obj.animation_key)

            # calculate fov
            maps.make_fov(self.current_map.map_tiles)
            globals.FOV_CALCULATE = True

    @property
    def objects_on_map(self):
        return self.current_map.list_of_objects

    def add_object(self, object_to_add):
        self.current_map.list_of_objects.append(object_to_add)

    def remove_object(self, object_to_remove):
        self.current_map.list_of_objects.remove(object_to_remove)


def main_loop():
    """
    Runs the game main loop
    """

    # get game state from global game object
    # substitute game_quit = False

    game_quit = False
    while not game_quit:

        # Handle Player Input
        player_action = handle_keys()

        # example of how to handle input based on game state
        # for event in pygame.event.get():
        #     input.update(event, game.State.get_current())
        #     ui.process_ui_events(event)
        #     ui.handle_ui_events(event)

        maps.calculate_fov()

        if player_action == 'QUIT':
            exit_game()

        # Process Turn Queue
        turn(player_action)

        if globals.PLAYER.state in ['STATUS DEAD', 'STATUS WIN']:
            try:
                os.remove('data/savegame')
            except OSError:
                pass
            game_quit = True

        # draw the game
        draw.game()

        # update the display
        pygame.display.flip()

        globals.CLOCK.tick(constants.GAME_FPS)


def turn(player_action):

    # get list of active actors on map
    # order turn queue based on actor initiative
    # select turn_holder

    # define game state based on type turn holder

    # if game_state == "player_turn":
    #     input = get_input()
    #     handle_input(turn_holder, input)  # have whatever input apply only to the turn holder
    # elif game_state == "enemy_turn":
    #     take_turn(turn_holder)  # have the ai run on the ai who is turn holder only

    if player_action != 'no-action':
        for obj in globals.GAME.objects_on_map:
            if obj.ai:
                obj.ai.take_turn()
            if obj.exit_portal:
                obj.exit_portal.update()


def handle_keys():
    """
    Handles player inputs
    """

    # get player input
    keys_list = pygame.key.get_pressed()
    events = pygame.event.get()

    # Check for mod key
    mod_key = keys_list[pygame.K_RSHIFT] or keys_list[pygame.K_LSHIFT]

    for event in events:
        # Quit game if player closes window
        if event.type == pygame.QUIT:
            return 'QUIT'
        if event.type == pygame.KEYDOWN:
            # moves up by pressing the "Up" key
            if event.key == pygame.K_UP:
                globals.PLAYER.creature.move(0, -1)
                globals.FOV_CALCULATE = True
                return 'player-moved'
            # moves down by pressing the "Down" key
            if event.key == pygame.K_DOWN:
                globals.PLAYER.creature.move(0, 1)
                globals.FOV_CALCULATE = True
                return 'player-moved'
            # moves left by pressing the "Left" key
            if event.key == pygame.K_LEFT:
                globals.PLAYER.creature.move(-1, 0)
                globals.FOV_CALCULATE = True
                return 'player-moved'
            # moves right by pressing the "Right" key
            if event.key == pygame.K_RIGHT:
                globals.PLAYER.creature.move(1, 0)
                globals.FOV_CALCULATE = True
                return 'player-moved'
            # Gets item from the ground by pressing the "g" key
            if event.key == pygame.K_g:
                objects_at_player = maps.objects_at_coordinates(globals.PLAYER.x, globals.PLAYER.y)
                for obj in objects_at_player:
                    if obj.item:
                        obj.item.pick_up(globals.PLAYER)
            # Drops first item in the inventory onto the ground by pressing the "d" key
            if event.key == pygame.K_d:
                if len(globals.PLAYER.container.inventory) > 0:
                    globals.PLAYER.container.inventory[-1].item.drop(globals.PLAYER.x, globals.PLAYER.y)
            # Pauses the game by pressing the "p" key
            if event.key == pygame.K_p:
                menu.pause()
            # Opens the inventory menu by pressing the "i" key
            if event.key == pygame.K_i:
                menu.inventory()
            # Open look menu by pressing the "l" key
            if event.key == pygame.K_l:
                menu.tile_select()
            # Go down or up stairs by pressing "SHIT + ."
            if mod_key and event.key == pygame.K_PERIOD:
                objects_at_player = maps.objects_at_coordinates(globals.PLAYER.x, globals.PLAYER.y)
                for obj in objects_at_player:
                    if obj.stairs:
                        obj.stairs.use()
                    if obj.exit_portal:
                        obj.exit_portal.use()

    return 'no-action'


def message(message_to_display, color=constants.COLOR_GREY):
    globals.GAME.message_history.append((message_to_display, color))


def start(continue_game=True):

    # starts the game
    if continue_game:
        try:
            load()
            globals.FOV_CALCULATE = True
        except FileNotFoundError:
            new()
            globals.FOV_CALCULATE = True
            print('Game not found')
    else:
        new()
        globals.FOV_CALCULATE = True
    main_loop()


def new():

    # Creates new GAME
    globals.GAME = ObjectGame()

    # initialize maps
    globals.GAME.current_map = maps.GameMap(constants.MAP_WIDTH, constants.MAP_HEIGHT)

    # Creates a player
    generator.player((0, 0))

    # Generate the map
    globals.GAME.current_map.generate_dungeon(
                constants.MAP_MAX_NUM_ROOMS,
                constants.ROOM_MIN_WIDTH, constants.ROOM_MAX_WIDTH,
                constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT
            )


def save():

    for obj in globals.GAME.objects_on_map:
        obj.animation_destroy()

    with gzip.open('data/savegame', 'wb') as file:
        pickle.dump([globals.GAME, globals.PLAYER], file)


def load():

    with gzip.open('data/savegame', 'rb') as file:
        globals.GAME, globals.PLAYER = pickle.load(file)

    for obj in globals.GAME.objects_on_map:
        obj.animation = globals.ASSETS.sprite(obj.animation_key)

    # make FOV
    maps.make_fov(globals.GAME.current_map)


def preferences_save():

    with gzip.open('data/preferences', 'wb') as file:
        pickle.dump(globals.PREFERENCES, file)


def preferences_load():

    with gzip.open('data/preferences', 'rb') as file:
        globals.PREFERENCES = pickle.load(file)


def exit_game():

    save()
    pygame.quit()
    sys.exit()
