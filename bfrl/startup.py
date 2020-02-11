# modules
import random
import pygame
import tcod

# game files
from bfrl import constants
from bfrl import game
from bfrl import globals
from bfrl import data
from bfrl import camera
from bfrl import assets


def init():

    # initialize pygame
    pygame.init()
    pygame.key.set_repeat(200, 70)
    globals.init()

    tcod.namegen_parse('data/namegen/celtic.cfg')

    # PREFERENCES tracks user preferences
    try:
        game.preferences_load()
    except FileNotFoundError:
        globals.PREFERENCES = data.Preferences()

    # create display surface with a given Height, and Width
    globals.SURFACE_MAIN = pygame.display.set_mode((constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT))

    globals.SURFACE_MAP = pygame.Surface((
        constants.MAP_WIDTH * constants.CELL_WIDTH,
        constants.MAP_HEIGHT * constants.CELL_HEIGHT
    ))

    # CAMERA tracks what is shown on the display
    globals.CAMERA = camera.ObjectCamera()

    # ASSETS stores the game assets
    globals.ASSETS = assets.Assets()

    # CLOCK tracks and limits CPU cycles
    globals.CLOCK = pygame.time.Clock()

    # RANDOM NUMBER ENGINE
    globals.RANDOM_ENGINE = random.SystemRandom()

    # When FOV is true, FOV recalculates
    globals.FOV_CALCULATE = True
