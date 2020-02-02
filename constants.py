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

# Sprites
S_PLAYER = pygame.image.load('data/python.png')
S_ENEMY = pygame.image.load('data/crab.png')
S_WALL = pygame.image.load('data/wall.jpg')
S_WALL_EXPLORED = pygame.image.load('data/wall_explored.png')
S_FLOOR = pygame.image.load('data/floor.png')
S_FLOOR_EXPLORED = pygame.image.load('data/floor_explored.png')

# FONTS
FONT_DEBUG_MESSAGE = pygame.font.Font('data/joystix.ttf', 20)

# FOV Settings
TORCH_RADIUS = 10
FOV_LIGHT_WALLS = True
FOV_ALGORITHM = tcod.FOV_BASIC
