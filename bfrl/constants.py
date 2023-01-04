import pygame
from pygame.color import Color
from pygame.font import Font

from bfrl.structs import Vector

pygame.init()

# Game Sizes
CAMERA_WIDTH: int = 1200
CAMERA_HEIGHT: int = 800
CAMERA_SIZE: Vector = Vector(CAMERA_WIDTH, CAMERA_HEIGHT)

CELL_WIDTH: int = 32
CELL_HEIGHT: int = 32
CELL_SIZE: Vector = Vector(CELL_WIDTH, CELL_HEIGHT)

# FPS Limit
GAME_FPS: int = 60

# Map Vars
MAP_WIDTH: int = 21
MAP_HEIGHT: int = 21
MAP_SIZE: Vector = Vector(MAP_WIDTH, MAP_HEIGHT)
MAP_SIZE_PX: Vector = MAP_SIZE.elementwise() * CELL_SIZE
MAP_MAX_NUM_ROOMS: int = 2
MAP_LEVELS: int = 2

# Room Limitations
ROOM_MAX_HEIGHT: int = 3
ROOM_MIN_HEIGHT: int = 3
ROOM_MAX_WIDTH: int = 3
ROOM_MIN_WIDTH: int = 3

# Color definitions
COLOR_BLACK: Color = Color(0, 0, 0)
COLOR_WHITE: Color = Color(255, 255, 255)
COLOR_GREY: Color = Color(100, 100, 100)
COLOR_RED: Color = Color(255, 0, 0)
COLOR_GREEN: Color = Color(0, 255, 0)

# Game colors
COLOR_DEFAULT_BG: Color = COLOR_GREY

# Message Defaults
NUM_MESSAGES: int = 4

# Fonts
FONT_TITLE_SCREEN = Font("data/joystix.ttf", 26)
FONT_DEBUG_MESSAGE = Font("data/joystix.ttf", 16)
FONT_MESSAGE_TEXT = Font("data/joystix.ttf", 12)
FONT_CURSOR_TEXT = Font("data/joystix.ttf", CELL_HEIGHT)

# Depths
DEPTH_PLAYER: int = -100
DEPTH_CREATURES: int = 1
DEPTH_ITEMS: int = 2
DEPTH_CORPSE: int = 100
DEPTH_STAIRS: int = 101
