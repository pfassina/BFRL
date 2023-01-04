import pygame

from bfrl import constants, draw, game
from bfrl import game_globals as gg
from bfrl import menu, structs


def main() -> None:

    assert gg.GAME
    assert gg.CLOCK

    while gg.GAME.state != game.GameState.QUIT:
        player_action = handle_keys()

        if player_action == game.PlayerAction.QUIT:
            gg.GAME.state = game.GameState.QUIT

        draw.game()

        pygame.display.flip()
        gg.CLOCK.tick(constants.GAME_FPS)


def handle_keys() -> game.PlayerAction:

    assert gg.GAME
    events = pygame.event.get()

    for event in events:
        # quits game if player closes window
        if event.type == pygame.QUIT:
            return game.PlayerAction.QUIT
        if event.type != pygame.KEYDOWN:
            continue

        assert gg.GAME.active_actor.creature

        # moves up by pressing the "Up" key
        if event.key == pygame.K_UP:
            gg.GAME.active_actor.creature.move(structs.Direction.NORTH)
            return game.PlayerAction.MOVED
        # moves down by pressing the "Down" key
        if event.key == pygame.K_DOWN:
            gg.GAME.active_actor.creature.move(structs.Direction.SOUTH)
            return game.PlayerAction.MOVED
        # moves left by pressing the "Left" key
        if event.key == pygame.K_LEFT:
            gg.GAME.active_actor.creature.move(structs.Direction.WEST)
            return game.PlayerAction.MOVED
        # moves right by pressing the "Right" key
        if event.key == pygame.K_RIGHT:
            gg.GAME.active_actor.creature.move(structs.Direction.EAST)
            return game.PlayerAction.MOVED
        # attack by pressing 'a'
        if event.key == pygame.K_a:
            target_tiles = menu.tile_select(
                origin=gg.GAME.active_actor.coord,
                max_range=gg.GAME.active_actor.creature.range,
                radius=gg.GAME.active_actor.creature.area_of_attack,
            )

            attacked = gg.GAME.active_actor.creature.attack(target_tiles)
            return game.PlayerAction.ATTACKED if attacked else game.PlayerAction.NONE
        # select cursor by pressing 'k'
        if event.key == pygame.K_k:
            menu.tile_select(gg.GAME.active_actor.coord)
            return game.PlayerAction.NONE
        # ends active actor turn by pressing the "Space" key
        if event.key == pygame.K_SPACE:
            gg.GAME.reset_turn()
            return game.PlayerAction.END_TURN
        # toggles the turn order pannel by pressing the "t" key
        if event.key == pygame.K_t:
            gg.GAME.toggle_panel("turn_order")
            return game.PlayerAction.NONE
        if event.key == pygame.K_m:
            gg.GAME.toggle_panel("messages")
            return game.PlayerAction.NONE
    return game.PlayerAction.NONE
