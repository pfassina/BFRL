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
        self.tile_dictionary = {
            'a': 1, 'b': 2, 'c': 3, 'd': 4,
            'e': 5, 'f': 6, 'g': 7, 'h': 8,
            'i': 9, 'j': 10, 'k': 11, 'l': 12,
            'm': 13, 'n': 14, 'o': 15, 'p': 16
        }

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
        image.blit(self.sprite_sheet, (0, 0), (self.tile_dictionary[column] * width, row * height, width, height))
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
            sprite_location_on_sheet = (self.tile_dictionary[column] * width + width * i, row * height, width, height)
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
        self.sound_adjust()

    def load_assets(self):

        def get_attributes(attribute_dictionary, actor=True):

            sprite_attributes = {
                'column': attribute_dictionary.get('column'),
                'row': attribute_dictionary.get('row'),
                'width': attribute_dictionary.get('width'),
                'height': attribute_dictionary.get('height'),
                'scale': attribute_dictionary.get('scale'),
            }
            if actor:
                sprite_attributes['num_sprites'] = attribute_dictionary.get('num_sprites')

            return sprite_attributes

        for category, assets in self.game_assets.items():
            for asset, attributes in assets.items():
                if category == 'sprite_sheets':
                    self.__setattr__(asset, SpriteSheet(attributes))
                elif category == 'tiles':
                    sheet = self.__getattribute__(attributes.get('sheet'))
                    tile_attributes = get_attributes(attributes, actor=False)
                    self.__setattr__(asset, sheet.get_image(**tile_attributes))
                elif category in ('characters', 'items', 'special'):
                    sheet = self.__getattribute__(attributes.get('sheet'))
                    asset_attributes = get_attributes(attributes)
                    self.__setattr__(asset, sheet.get_animation(**asset_attributes))
                elif category == 'bg_image':
                    image = pygame.image.load(attributes['image'])
                    scale = (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT)
                    image_scaled = pygame.transform.scale(image, scale)
                    self.__setattr__(asset, image_scaled)
                elif category == 'music':
                    self.__setattr__(asset, attributes)
                elif category == 'sound':
                    sound_type = attributes.get('type')
                    sound_path = attributes.get('path')
                    self.__setattr__(asset, self.sound_add(sound_path))
                    if sound_type == 'hit':
                        self.sound_hit_list.append(self.__getattribute__(asset))

    def sprite(self, key):

        sprite_dictionary = {}
        for category in self.game_assets.values():
            for asset in category.keys():
                sprite_dictionary[asset] = self.__getattribute__(asset)

        return sprite_dictionary[key]

    def sound_add(self, file):
        new_sound = pygame.mixer.Sound(file)
        self.sound_list.append(new_sound)
        return new_sound

    def sound_adjust(self):

        for sound in self.sound_list:
            sound.set_volume(globals.PREFERENCES.volume_sound)

        pygame.mixer.music.set_volume(globals.PREFERENCES.volume_music)
