from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pygame import Surface

from bfrl import constants
from bfrl import game_globals as gg
from bfrl.structs import Direction, SpriteType, Vector


@dataclass
class Actor:
    name: str
    coord: Vector
    sprite_type: SpriteType
    animation_speed: float = 1.0
    depth: int = 0

    def __post_init__(self) -> None:

        assert gg.ASSETS

        self.origin: Vector = self.coord

        self._animation = gg.ASSETS.sprite(self.sprite_type)
        self._animation_len: int = len(self._animation)
        self._frame: int = 0
        self._flicker_timer: float = 0.0
        self._flicker_speed: float = self.animation_speed / self._animation_len

        # components
        self.creature: Optional[CreatureComponent] = None

    def draw(self) -> None:

        assert gg.SURFACE_MAP
        assert self._animation

        self._update_animation()
        sprite: Surface = self._animation[self._frame]
        cell_position: Vector = self.coord.elementwise() * constants.CELL_SIZE
        gg.SURFACE_MAP.blit(sprite, cell_position)

    def add_component(self, component) -> None:
        if isinstance(component, CreatureComponent):
            self.creature = component
            self.creature.owner = self

    @property
    def initiative(self) -> int:
        assert self.creature
        return self.creature.initiative

    def delay(self, delay: int) -> None:
        assert self.creature
        self.creature.initiative += delay

    def end_movement(self) -> None:
        assert self.creature
        self.creature.initiative += self.creature.delay
        self.creature.delay = 0
        self.origin = self.coord

    def destroy(self) -> None:
        assert gg.GAME
        self._animation = None
        gg.GAME.current_map.remove_object(self)

    def _update_animation(self) -> None:

        assert gg.CLOCK

        if self._animation_len == 1:
            return

        if gg.CLOCK.get_fps() == 0.0:
            return

        self._flicker_timer += 1 / gg.CLOCK.get_fps()

        if self._flicker_timer < self._flicker_speed:
            return

        self._flicker_timer = 0.0
        self._frame = (self._frame + 1) % self._animation_len

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Actor):
            raise TypeError
        return self.name == __o.name

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, Actor):
            raise TypeError
        assert self.creature and __o.creature
        return self.creature < __o.creature


class Component:
    def __init__(self) -> None:
        self.owner: Optional[Actor] = None


@dataclass
class CreatureComponent(Component):
    initiative: int
    health: int = 10
    strength: int = 2
    range: int = 1
    area_of_attack: int = 0

    def __post_init__(self) -> None:
        super().__init__()
        self.delay: int = 0

    def move(self, direction: Direction) -> None:

        if not self.owner:
            raise NameError
        if not gg.GAME:
            raise NameError

        target = self.owner.coord + direction.value

        if gg.GAME.current_map.check_for_wall(target):
            return

        if gg.GAME.current_map.check_for_object(target):
            return

        if self.owner.origin.distance(target) > gg.GAME.time_left + 1:
            return

        self.delay = int(self.owner.origin.distance(target))
        self.owner.coord = target

    def take_damage(self, damage: int) -> None:
        assert self.owner
        self.health -= damage
        self.owner.delay(damage)
        if self.health > 0:
            return
        self.owner.destroy()

    def attack(self, tiles: list[Vector]) -> bool:

        assert gg.GAME
        assert self.owner

        attacked = False
        for tile in tiles:

            target = gg.GAME.current_map.check_for_object(tile)

            if not target:
                continue
            if not target.creature:
                continue
            if target == self.owner:
                continue

            attacked = True
            target.creature.take_damage(self.strength)
            self.owner.delay(20)

            gg.GAME.message(
                f"{self.owner.name} attacked {target.name} for {self.strength} damage."
            )

        if not attacked:
            return False

        self.owner.end_movement()
        return True

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, CreatureComponent):
            raise TypeError
        return self.initiative < __o.initiative
