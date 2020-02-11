# modules
import pygame
import yaml

# game files
# from bfrl import startup
from bfrl import constants
from bfrl import globals


class SpriteSheet:
    """
    Class used to grab images out of a sprite sheet. As a class, it allows you to access and subdivide portions of the
    sprite_sheet.

    ** PROPERTIES **
    ObjectSpriteSheet.sprite_sheet : The loaded spritesheet accessed through the file_name argument.
    """

    def __init__(self, file_name):
        """
        :param file_name: String which contains the directory/filename of the image for use as a spritesheet.
        """
        # load sprite sheet
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, column, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, scale=None):
        """
        returns a list containing a single image from a spritesheet given a grid location.
        :param column: Letter which gets converted into an integer
        :param row: integer
        :param width: integer, individual image width in pixels
        :param height: integer, individual sprite height in pixels
        :param scale: Tuple (width, height).  If included, scales the images to a new size
        :return: list of sprites to be animated
        """

        image = pygame.Surface([width, height]).convert()
        image.blit(self.sprite_sheet, (0, 0), (column * width, row * height, width, height))
        image.set_colorkey(constants.COLOR_BLACK)

        if scale:
            (new_width, new_height) = scale
            image = pygame.transform.scale(image, (new_width, new_height))

        return image

    def get_animation(self, column, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, num_sprites=1,
                      scale=None):
        """
        returns a list containing a sequence of images starting from a grid location.
        :param column: Letter which gets converted into an integer
        :param row: integer
        :param width: integer, individual image width in pixels
        :param height: integer, individual sprite height in pixels
        :param num_sprites: number of sprites on an animation
        :param scale: Tuple (width, height).  If included, scales the images to a new size
        :return: list of sprites to be animated
        """

        sprite_list = []
        for i in range(num_sprites):

            # create blank image
            image = pygame.Surface([width, height]).convert()

            # copy image from sheet onto blank
            sprite_location_on_sheet = (column * width + width * i, row * height, width, height)
            image.blit(self.sprite_sheet, (0, 0), sprite_location_on_sheet)

            # set transparency key to black
            image.set_colorkey(constants.COLOR_BLACK)

            if scale:
                (new_width, new_height) = scale
                image = pygame.transform.scale(image, (new_width, new_height))

            sprite_list.append(image)

        return sprite_list


class Assets:
    """
    This class is a structure that holds all assets used in the game. This includes sprites, sound effects, and music.
    """

    def __init__(self):

        with open('data/assets.yaml', 'r') as assets_file:
            self.game_assets = yaml.full_load(assets_file)

        self.sound_list = []
        self.sound_hit_list = []

        self.load_assets()
        self.sprite_dictionary = {}
        self.generate_sprite_dictionary()

        self.sound_adjust()

    def load_assets(self):

        # load sheets
        sheets = self.game_assets.get('sprite_sheets')
        for name, path in sheets.items():
            self.__setattr__(name, SpriteSheet(path))

        # load walls
        wall_assets = self.game_assets.get('walls')
        walls_tiles = self.get_wall_tiles(wall_assets)
        self.__setattr__('walls', walls_tiles)

        # load tiles
        tiles = self.game_assets.get('tiles')
        for tile, attributes in tiles.items():
            sheet = self.__getattribute__(attributes.pop('sheet'))
            self.__setattr__(tile, sheet.get_image(**attributes))

        # load characters
        characters = self.game_assets.get('characters')
        for character, attributes in characters.items():
            sheet = self.__getattribute__(attributes.pop('sheet'))
            self.__setattr__(character, sheet.get_animation(**attributes))

        # load items
        items = self.game_assets.get('items')
        for item, attributes in items.items():
            sheet = self.__getattribute__(attributes.pop('sheet'))
            self.__setattr__(item, sheet.get_animation(**attributes))

        # load special
        specials = self.game_assets.get('specials')
        for special, attributes in specials.items():
            sheet = self.__getattribute__(attributes.pop('sheet'))
            self.__setattr__(special, sheet.get_animation(**attributes))

        # load background images
        bg_images = self.game_assets.get('bg_images')
        for bg_image, attributes in bg_images.items():
            image = pygame.image.load(attributes['image'])
            scale = (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT)
            image_scaled = pygame.transform.scale(image, scale)
            self.__setattr__(bg_image, image_scaled)

        # load music
        music = self.game_assets.get('music')
        for song, path in music.items():
            self.__setattr__(song, path)

        # load sounds
        sounds = self.game_assets.get('sounds')
        for sound, attributes in sounds.items():
            sound_type = attributes.get('type')
            sound_path = attributes.get('path')
            self.__setattr__(sound, self.sound_add(sound_path))
            if sound_type == 'hit':
                self.sound_hit_list.append(self.__getattribute__(sound))

    def get_wall_tiles(self, wall_assets):

        # Create Wall Dictionary using bitwise localization for each wall face
        wall_tiles = {}
        for wall_type, attributes in wall_assets.items():
            wall_tiles[wall_type] = {}
            sprite_sheet = self.__getattribute__(attributes.get('sheet'))
            wall_width = attributes.get('width')
            wall_height = attributes.get('height')
            wall_scale = attributes.get('scale')

            sprites = attributes.get('sprites')
            for facing, coordinates in sprites.items():
                tile_attributes = {
                    'column': coordinates[0],
                    'row': coordinates[1],
                    'width': wall_width,
                    'height': wall_height,
                    'scale': wall_scale,
                }
                wall_tiles[wall_type][facing] = sprite_sheet.get_image(**tile_attributes)

        return wall_tiles

    def generate_sprite_dictionary(self):

        sprite_dict = {}
        for category, assets in self.game_assets.items():
            if category != 'walls':
                for asset, attributes in assets.items():
                    sprite_dict[asset] = self.__getattribute__(asset)
            else:
                sprite_dict['walls'] = {'default': 0, 'explored': 0}
                sprite_dict['walls']['default'] = self.__getattribute__('walls')['default']
                sprite_dict['walls']['explored'] = self.__getattribute__('walls')['explored']

        self.sprite_dictionary = sprite_dict


    def sprite(self, key):
        return self.sprite_dictionary[key]

    def sound_add(self, file):
        new_sound = pygame.mixer.Sound(file)
        self.sound_list.append(new_sound)
        return new_sound

    def sound_adjust(self):

        for sound in self.sound_list:
            sound.set_volume(globals.PREFERENCES.volume_sound)

        pygame.mixer.music.set_volume(globals.PREFERENCES.volume_music)
