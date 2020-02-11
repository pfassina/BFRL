# modules
from datetime import date
import pygame

# game files
from bfrl import constants
from bfrl import game
from bfrl import globals
from bfrl import draw


def player(dead_player):

    dead_player.state = 'STATUS DEAD'

    globals.SURFACE_MAIN.fill(constants.COLOR_BLACK)
    death_text = {
        'display_surface': globals.SURFACE_MAIN,
        'text_to_display': 'YOU DIED!',
        'font': constants.FONT_TITLE_SCREEN,
        'coordinates': (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2),
        'text_color': constants.COLOR_WHITE,
        'alignment': 'center',
    }
    draw.text(**death_text)

    filename = f"{globals.PLAYER.display_name}-{date.today().strftime('%Y%m%d')}.txt"
    with open(f'data/legacy/{filename}', 'a+') as legacy_file:
        for msg, _ in globals.GAME.message_history:
            legacy_file.write(f'{msg}\n')

    milliseconds_passed = 0
    while milliseconds_passed <= 2000:
        pygame.event.get()
        milliseconds_passed += globals.CLOCK.tick(constants.GAME_FPS)
        pygame.display.update()


def monster(dead_monster):
    """
    On death, most monsters stop moving.
    :param dead_monster: Monster instance
    """

    message = f'{dead_monster.creature.name_instance} is dead!'
    game.message(message, constants.COLOR_GREY)
    dead_monster.animation_key = 'S_FLESH_01'
    dead_monster.animation = globals.ASSETS.sprite('S_FLESH_01')
    dead_monster.depth = constants.DEPTH_CORPSE
    dead_monster.creature = None
    dead_monster.ai = None


def mouse(dead_mouse):

    message = f'{dead_mouse.creature.name_instance} is dead! A delicious corpse drops to the ground.'
    game.message(message, constants.COLOR_GREY)
    dead_mouse.animation_key = 'S_FLESH_02'
    dead_mouse.animation = globals.ASSETS.sprite('S_FLESH_02')
    dead_mouse.name_object = 'Yummy meat'
    dead_mouse.depth = constants.DEPTH_CORPSE
    dead_mouse.creature = None
    dead_mouse.ai = None
