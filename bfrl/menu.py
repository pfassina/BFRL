# standard libraries
import pygame
import sys

# game files
from bfrl import constants
from bfrl import draw
from bfrl import game
from bfrl import globals
from bfrl import maps


def main():

    # UI Addresses
    center_x, center_y = (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2)
    game_tile_x, game_tile_y = (center_x, center_y - 260)
    footer_x, footer_y = (center_x - 500, constants.CAMERA_HEIGHT - 10)
    continue_x, continue_y = (center_x, center_y + 240)
    new_game_x, new_game_y = (center_x, continue_y + 40)
    options_x, options_y = (center_x, new_game_y + 40)
    exit_x, exit_y = (center_x, options_y + 40)

    game_title = {
        'display_surface': globals.SURFACE_MAIN,
        'text_to_display': 'PythonRL',
        'font': constants.FONT_TITLE_SCREEN,
        'coordinates': (game_tile_x, game_tile_y),
        'text_color': constants.COLOR_WHITE,
        'back_color': constants.COLOR_BLACK,
        'alignment': 'center',
    }

    footer = {
        'display_surface': globals.SURFACE_MAIN,
        'text_to_display': 'music by icons8.com',
        'font': constants.FONT_MESSAGE_TEXT,
        'coordinates': (footer_x, footer_y),
        'text_color': constants.COLOR_GREY,
        'alignment': 'center',
    }

    continue_button_attributes = {
        'surface': globals.SURFACE_MAIN,
        'button_text': 'continue',
        'size': (150, 35),
        'center_coordinates': (continue_x, continue_y)
    }
    continue_button = draw.UIButton(**continue_button_attributes)

    new_game_button_attributes = {
        'surface': globals.SURFACE_MAIN,
        'button_text': 'new game',
        'size': (150, 35),
        'center_coordinates': (new_game_x, new_game_y)
    }
    new_game_button = draw.UIButton(**new_game_button_attributes)

    options_attributes = {
        'surface': globals.SURFACE_MAIN,
        'button_text': 'options',
        'size': (150, 35),
        'center_coordinates': (options_x, options_y)
    }
    options_button = draw.UIButton(**options_attributes)

    quit_button_attributes = {
        'surface': globals.SURFACE_MAIN,
        'button_text': 'quit game',
        'size': (150, 35),
        'center_coordinates': (exit_x, exit_y)
    }
    quit_button = draw.UIButton(**quit_button_attributes)

    # loads theme music
    pygame.mixer.music.load(globals.ASSETS.music_background)
    pygame.mixer.music.play(loops=-1)

    menu_running = True
    while menu_running:

        list_of_events = pygame.event.get()
        mouse_position = pygame.mouse.get_pos()

        game_input = (list_of_events, mouse_position)

        for event in list_of_events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # button updates
        if continue_button.update(game_input):
            pygame.mixer.music.stop()
            game.start(continue_game=True)

        if new_game_button.update(game_input):
            pygame.mixer.music.stop()
            game.start(continue_game=False)

        if options_button.update(game_input):
            options()

        if quit_button.update(game_input):
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()

        # draw menu
        globals.SURFACE_MAIN.blit(globals.ASSETS.main_menu_bg, (0, 0))
        draw.text(**game_title)
        draw.text(**footer)

        # update surfaces
        continue_button.draw()
        new_game_button.draw()
        options_button.draw()
        quit_button.draw()
        pygame.display.update()


def options():

    window_center = (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2)

    settings_menu_width = 200
    settings_menu_height = 200
    settings_menu_bgcolor = constants.COLOR_DEFAULT_BG

    settings_menu_surface = pygame.Surface((settings_menu_width, settings_menu_height))
    settings_menu_rect = pygame.Rect(0, 0, settings_menu_width, settings_menu_width)
    settings_menu_rect.center = window_center
    menu_center_x, menu_center_y = settings_menu_rect.center

    # Define Sound Settings Slider
    slider_sound_text = {
        'display_surface': globals.SURFACE_MAIN,
        'text_to_display': 'sound',
        'font': constants.FONT_MESSAGE_TEXT,
        'coordinates': (menu_center_x, menu_center_y - 60),
        'text_color': constants.COLOR_WHITE,
        'alignment': 'center',
    }
    slider_sound_attributes = {
        'size': (125, 15),
        'surface': globals.SURFACE_MAIN,
        'center_coordinates': (menu_center_x, menu_center_y - 40),
        'color_background': constants.COLOR_WHITE,
        'color_foreground': constants.COLOR_GREEN,
        'value': globals.PREFERENCES.volume_sound
    }
    slider_sound = draw.UISlider(**slider_sound_attributes)

    # Define Music Settings Slider
    slider_music_text = {
        'display_surface': globals.SURFACE_MAIN,
        'text_to_display': 'music',
        'font': constants.FONT_MESSAGE_TEXT,
        'coordinates': (menu_center_x, menu_center_y),
        'text_color': constants.COLOR_WHITE,
        'alignment': 'center',
    }
    slider_music_attributes = {
        'size': (125, 15),
        'surface': globals.SURFACE_MAIN,
        'center_coordinates': (menu_center_x, menu_center_y + 20),
        'color_background': constants.COLOR_WHITE,
        'color_foreground': constants.COLOR_GREEN,
        'value': globals.PREFERENCES.volume_music
    }
    slider_music = draw.UISlider(**slider_music_attributes)

    # Create save globals.PREFERENCES button
    save_preferences_button_attributes = {
        'surface': globals.SURFACE_MAIN,
        'button_text': 'save',
        'size': (100, 35),
        'center_coordinates': (menu_center_x, menu_center_y + 70)
    }
    save_preferences_button = draw.UIButton(**save_preferences_button_attributes)

    menu_close = False
    while not menu_close:

        list_of_events = pygame.event.get()
        mouse_position = pygame.mouse.get_pos()

        game_input = (list_of_events, mouse_position)

        # for event in list_of_events:
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_ESCAPE:
        #             menu_close = True

        slider_sound.update(game_input)
        if globals.PREFERENCES.volume_sound != slider_sound.value:
            globals.PREFERENCES.volume_sound = slider_sound.value
            globals.ASSETS.sound_adjust()

        slider_music.update(game_input)
        if globals.PREFERENCES.volume_music != slider_music.value:
            globals.PREFERENCES.volume_music = slider_music.value
            globals.ASSETS.sound_adjust()

        if save_preferences_button.update(game_input):
            game.preferences_save()
            menu_close = True

        settings_menu_surface.fill(settings_menu_bgcolor)
        globals.SURFACE_MAIN.blit(settings_menu_surface, settings_menu_rect.topleft)

        draw.text(**slider_sound_text)
        slider_sound.draw()

        draw.text(**slider_music_text)
        slider_music.draw()

        save_preferences_button.draw()

        pygame.display.update()


def pause():
    """
    This menu pauses the game and displays a simple message
    """

    menu_close = False

    window_width = constants.CAMERA_WIDTH
    window_height = constants.CAMERA_HEIGHT

    menu_text = 'PAUSED'
    menu_font = constants.FONT_DEBUG_MESSAGE

    text_height = draw.helper_text_height(menu_font)
    text_width = draw.helper_text_width(menu_font) * len(menu_text)

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
        draw.text(globals.SURFACE_MAIN, menu_text, constants.FONT_DEBUG_MESSAGE, text_location, font_color, bg_color)
        globals.CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()


def inventory():

    menu_width = 200
    menu_height = 200

    window_width = constants.CAMERA_WIDTH
    window_height = constants.CAMERA_HEIGHT

    menu_x = int(window_width/2 - menu_width/2)
    menu_y = int(window_height/2 - menu_height/2)

    menu_location = (menu_x, menu_y)

    menu_font = constants.FONT_MESSAGE_TEXT
    menu_text_height = draw.helper_text_height(menu_font)

    inventory_surface = pygame.Surface((menu_width, menu_height))

    menu_close = False
    while not menu_close:

        menu_font = constants.FONT_MESSAGE_TEXT
        menu_font_color = constants.COLOR_WHITE
        menu_bg_color = constants.COLOR_BLACK
        menu_mouse_over_bg = constants.COLOR_GREY

        # Clear the menu
        inventory_surface.fill(constants.COLOR_BLACK)

        # Collect list of item names
        item_list = [item.display_name for item in globals.PLAYER.container.inventory]

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
                    globals.PLAYER.container.inventory[mouse_line_selection].item.use()
                    # TODO keep inventory open if item is an equipment
                    menu_close = True

        # Draw item list
        for line, name in enumerate(item_list):
            name_location = (0, 0 + line * menu_text_height)
            if line == mouse_line_selection and mouse_in_window:
                draw.text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_mouse_over_bg)
            else:
                draw.text(inventory_surface, name, menu_font, name_location, menu_font_color, menu_bg_color)

        # Render Game

        draw.game()

        # Display Menu
        globals.SURFACE_MAIN.blit(inventory_surface, menu_location)
        pygame.display.flip()


def tile_select(origin=None, max_range=None, ignore_walls=True, ignore_creatures=True, radius=None):
    """
    This menu lets the player select a tile on the map.
    The game pauses, produces a screen rectangle, and returns the map address when the LMB is clicked.
    :return: (x,y) map address tuple
    """

    menu_close = False
    while not menu_close:

        # get mouse position
        mouse_coordinates = pygame.mouse.get_pos()
        map_coordinate_x, map_coordinate_y = globals.CAMERA.window_to_map(mouse_coordinates)

        map_address_x = int(map_coordinate_x / constants.CELL_WIDTH)
        map_address_y = int(map_coordinate_y / constants.CELL_HEIGHT)

        if origin:
            list_of_tiles = maps.find_line(origin, (map_address_x, map_address_y))
        else:
            list_of_tiles = [(map_address_x, map_address_y)]

        if max_range:
            list_of_tiles = list_of_tiles[:max_range + 1]

        for i, (x, y) in enumerate(list_of_tiles):
            if i == 0:
                continue
            if not ignore_walls and maps.check_for_wall(globals.GAME.current_map, x, y):
                list_of_tiles = list_of_tiles[:i + 1]
                break
            if not ignore_creatures and maps.check_for_creature(x, y):
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
        globals.SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
        globals.SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

        globals.CAMERA.update()

        # draw the map first
        draw.map_surface(globals.GAME.current_map)
        for obj in globals.GAME.current_objects:
            obj.draw()

        # draw rectangle at mouse position on top of game
        if len(list_of_tiles) > 1:
            for tile in list_of_tiles[1:]:
                if tile == list_of_tiles[-1]:
                    draw.tile_rect(tile, marker='X')
                else:
                    draw.tile_rect(tile)

            # TODO: Show radius if len = 1
            if radius:
                area_of_effect = maps.find_radius(list_of_tiles[-1], radius)
                for x, y in area_of_effect:
                    draw.tile_rect((x, y), tile_color=constants.COLOR_RED)

        else:
            draw.tile_rect((map_address_x, map_address_y), marker='X')

        # update main surface with the new map
        globals.SURFACE_MAIN.blit(globals.SURFACE_MAP, (0, 0), globals.CAMERA.rectangle)

        draw.debug()
        draw.messages()

        pygame.display.flip()
        globals.CLOCK.tick(constants.GAME_FPS)
