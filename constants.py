import tcod
import pygame

pygame.init()


# Game Sizes
CAMERA_WIDTH = 1200
CAMERA_HEIGHT = 800
CELL_WIDTH = 32
CELL_HEIGHT = 32

# FPS LIMIT
GAME_FPS = 60

# Map Vars
MAP_WIDTH = 50
MAP_HEIGHT = 30
MAP_MAX_NUM_ROOMS = 10

# Room Limitations
ROOM_MAX_HEIGHT = 7
ROOM_MIN_HEIGHT = 3
ROOM_MAX_WIDTH = 5
ROOM_MIN_WIDTH = 3

# Color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

# Game colors
COLOR_DEFAULT_BG = COLOR_GREY

# Message Defaults
NUM_MESSAGES = 4

# FOV Settings
TORCH_RADIUS = 10
FOV_LIGHT_WALLS = True
FOV_ALGORITHM = tcod.FOV_BASIC

# Fonts
FONT_TITLE_SCREEN = pygame.font.Font('data/joystix.ttf', 26)
FONT_DEBUG_MESSAGE = pygame.font.Font('data/joystix.ttf', 16)
FONT_MESSAGE_TEXT = pygame.font.Font('data/joystix.ttf', 12)
FONT_CURSOR_TEXT = pygame.font.Font('data/joystix.ttf', CELL_HEIGHT)
