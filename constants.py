import pygame
import tcod

pygame.init()

# Game Sizes
GAME_WIDTH = 800
GAME_HEIGHT = 600
CELL_WIDTH = 32
CELL_HEIGHT = 32

# FPS LIMIT
GAME_FPS = 60

# Map Vars
MAP_WIDTH = 20
MAP_HEIGHT = 20

# Color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (100, 100, 100)
COLOR_RED = (255, 0, 0)

# Game colors
COLOR_DEFAULT_BG = COLOR_GREY

# Message Defaults
NUM_MESSAGES = 4

# FOV Settings
TORCH_RADIUS = 10
FOV_LIGHT_WALLS = True
FOV_ALGORITHM = tcod.FOV_BASIC
