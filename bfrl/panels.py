from pygame import Surface

from bfrl import constants, draw
from bfrl import game_globals as gg
from bfrl.structs import Vector


def turn_order() -> None:

    assert gg.SURFACE_MAIN
    assert gg.GAME

    panel_size = Vector(200, constants.CAMERA_HEIGHT)
    panel_coord = Vector(constants.CAMERA_WIDTH - 200, 0)

    panel_surface = Surface(panel_size)
    panel_surface.fill(constants.COLOR_BLACK)

    draw.text(
        "Turn Order",
        panel_surface,
        constants.FONT_MESSAGE_TEXT,
        Vector(0, 0),
        constants.COLOR_WHITE,
        constants.COLOR_BLACK,
    )

    for line, actor in enumerate(gg.GAME.turn_order, 1):

        assert actor.creature
        text_coord = Vector(0, line * 16)
        text = f"{line}: {actor.name} ({actor.initiative} + {actor.creature.delay})"

        draw.text(
            text,
            panel_surface,
            constants.FONT_MESSAGE_TEXT,
            text_coord,
            constants.COLOR_WHITE,
            constants.COLOR_BLACK,
        )

    gg.SURFACE_MAIN.blit(panel_surface, panel_coord)


def messages() -> None:

    assert gg.SURFACE_MAIN
    assert gg.GAME

    panel_size = Vector(constants.CAMERA_WIDTH, 20)
    panel_coord = Vector(0, constants.CAMERA_HEIGHT - 20)

    panel_surface = Surface(panel_size)
    panel_surface.fill(constants.COLOR_BLACK)

    draw.text(
        gg.GAME.last_message,
        panel_surface,
        constants.FONT_MESSAGE_TEXT,
        Vector(0, 2),
        constants.COLOR_WHITE,
        constants.COLOR_BLACK,
    )

    gg.SURFACE_MAIN.blit(panel_surface, panel_coord)


def character() -> None:

    assert gg.SURFACE_MAIN
    assert gg.GAME

    panel_size = Vector(120, 3)
    panel_coord = Vector(10, constants.CAMERA_HEIGHT - 70)

    panel_surface = Surface(panel_size)
    panel_surface.fill(constants.COLOR_BLACK)

    assert gg.GAME.active_actor.creature

    name = gg.GAME.active_actor.name
    health = f"Health: {gg.GAME.active_actor.creature.health}"

    draw.text(
        name,
        panel_surface,
        constants.FONT_MESSAGE_TEXT,
        Vector(2, 0),
        constants.COLOR_WHITE,
        constants.COLOR_BLACK,
    )
    draw.text(
        health,
        panel_surface,
        constants.FONT_MESSAGE_TEXT,
        Vector(2, 16),
        constants.COLOR_WHITE,
        constants.COLOR_BLACK,
    )
    gg.SURFACE_MAIN.blit(panel_surface, panel_coord)
