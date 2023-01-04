import pygame
import yaml

from bfrl import assets, constants, game
from bfrl import game_globals as gg
from bfrl import generator, maps


def init() -> None:

    pygame.init()
    pygame.display.set_caption("BattleFortune Roguelike")
    pygame.key.set_repeat(200, 70)

    gg.init()

    gg.SURFACE_MAIN = pygame.display.set_mode(constants.CAMERA_SIZE)
    gg.SURFACE_MAP = pygame.Surface(constants.MAP_SIZE_PX)
    gg.ASSETS = assets.Assets()
    gg.CLOCK = pygame.time.Clock()


def new() -> None:

    state = game.GameState.PLAYER

    with open("data/scenario.yaml", "r") as file:
        data = yaml.full_load(file)

    scenario = game.Scenario(data["map"], data["actors"])

    current_map = maps.GameMap(scenario.size, scenario.tiles)
    gg.GAME = game.GameObject(current_map, state)
    generator.creatures(scenario.actors)

    gg.GAME.reset_turn()
