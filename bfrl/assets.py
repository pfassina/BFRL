# modules
from dataclasses import dataclass

import pygame
import yaml
from pygame import Rect, Surface
from pygame.mixer import Sound

from bfrl import constants
from bfrl.structs import SpriteType, TileType, Vector


@dataclass
class TileSprite:
    type: TileType
    explored: bool
    facing: int
    coord: Vector
    size: Vector
    scale: tuple[int, int]

    @property
    def top_left(self) -> Vector:
        return self.coord.elementwise() * self.size

    @property
    def rect(self) -> Rect:
        return Rect(self.top_left, self.size)


@dataclass
class Sprite:
    name: SpriteType
    coord: Vector
    size: Vector
    num_sprites: int
    scale: tuple[int, int]

    @property
    def top_left(self) -> Vector:
        return self.coord.elementwise() * self.size

    @property
    def rect(self) -> Rect:
        return Rect(self.top_left, self.size)


class SpriteSheet:
    def __init__(self, file_name: str) -> None:

        # load sprite sheet
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_tile(self, tile: TileSprite) -> Surface:

        image = Surface(tile.size).convert()
        image.blit(self.sprite_sheet, (0, 0), tile.rect)
        image.set_colorkey(constants.COLOR_BLACK)
        image = pygame.transform.scale(image, tile.scale)

        return image

    def get_sprite(self, sprite: Sprite) -> list[Surface]:

        sprite_list = []
        for i in range(sprite.num_sprites):

            # create blank image
            image = Surface(sprite.size).convert()

            # copy image from sheet onto blank
            offset = Vector(0, sprite.size.y * i)
            sprite_location_on_sheet = sprite.rect.move(offset)

            image.blit(self.sprite_sheet, (0, 0), sprite_location_on_sheet)

            # set transparency key to black
            image.set_colorkey(constants.COLOR_BLACK)

            image = pygame.transform.scale(image, sprite.scale)

            sprite_list.append(image)

        return sprite_list


class Assets:

    _sheets: dict[str, SpriteSheet]
    _tiles: dict[tuple[TileType, bool, int], Surface]
    _sprites: dict[SpriteType, list[Surface]]
    _images: dict[str, Surface]
    _music: dict[str, Sound]
    _sounds: dict[str, list[Sound]]

    def __init__(self):

        with open("data/assets.yaml", "r") as assets_file:
            self._game_assets = yaml.full_load(assets_file)

        self._load_assets()

    def tile(self, name: TileType, explored: bool, facing: int) -> Surface:
        return self._tiles[(name, explored, facing)]

    def sprite(self, name: SpriteType) -> list[Surface]:
        return self._sprites[name]

    @property
    def sound_list(self) -> list[Sound]:
        music_list = list(self._music.values())
        sound_list = [s for sl in self._sounds.values() for s in sl]
        return music_list + sound_list

    def _load_assets(self):

        self._sheets = self._load_sheets()
        self._tiles = self._load_tiles()
        self._sprites = self._load_sprites()

        self._images = self._load_images()
        self._music = self._load_music()
        self._sounds = self.__load_sounds()

    def _load_sheets(self) -> dict[str, SpriteSheet]:
        sheets: dict[str, str] = self._game_assets.get("sprite_sheets")
        return {name: SpriteSheet(path) for name, path in sheets.items()}

    def _load_tiles(self) -> dict[tuple[TileType, bool, int], Surface]:
        tiles = {}
        for attributes in self._game_assets["tiles"]:
            sheet: SpriteSheet = self._sheets[attributes["sheet"]]
            name: TileType = TileType[attributes["name"]]
            exp: bool = attributes["explored"]
            size: Vector = Vector(*attributes["size"])
            scale: tuple[int, int] = tuple(attributes["scale"])
            sprites: dict[int, list[int]] = attributes["sprites"]
            for facing, (col, row) in sprites.items():
                tile = TileSprite(name, exp, facing, Vector(col, row), size, scale)
                tiles[(name, exp, facing)] = sheet.get_tile(tile)
        return tiles

    def _load_sprites(self) -> dict[SpriteType, list[Surface]]:
        sprites = {}
        for category in ["characters", "items", "specials"]:
            for sprite_type, attributes in self._game_assets[category].items():
                name: SpriteType = SpriteType[sprite_type]
                sheet: SpriteSheet = self._sheets[attributes["sheet"]]
                coord: Vector = Vector(*attributes["coord"])
                size: Vector = Vector(*attributes["size"])
                num: int = attributes["num_sprites"]
                scale: tuple[int, int] = tuple(attributes["scale"])
                sprite = Sprite(name, coord, size, num, scale)
                sprites[name] = sheet.get_sprite(sprite)
        return sprites

    def _load_images(self) -> dict[str, Surface]:
        images = self._game_assets["images"]
        return {k: self._scale_image(v["path"]) for k, v in images.items()}

    def _load_music(self) -> dict[str, Sound]:
        music = self._game_assets["music"]
        return {k: self._load_sound(v) for k, v in music.items()}

    def __load_sounds(self) -> dict[str, list[Sound]]:
        sounds = self._game_assets.get("sounds")
        return {t: [self._load_sound(s) for s in l] for t, l in sounds.items()}

    @staticmethod
    def _scale_image(path) -> Surface:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, constants.CAMERA_SIZE)

    @staticmethod
    def _load_sound(path) -> Sound:
        return Sound(path)
