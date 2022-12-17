# modules
import pygame

# game files
from bfrl import constants
from bfrl import globals


class ObjectCamera:

    def __init__(self):

        self.width = constants.CAMERA_WIDTH
        self.height = constants.CAMERA_HEIGHT
        self.x, self.y = (0, 0)

    @property
    def rectangle(self):
        camera_rectangle = pygame.Rect((0, 0), (self.width, self.height))
        camera_rectangle.center = (self.x, self.y)
        return camera_rectangle

    @property
    def map_address(self):
        map_x = int(self.x / constants.CELL_WIDTH)
        map_y = int(self.y / constants.CELL_HEIGHT)

        return map_x, map_y

    def update(self):

        target_x = globals.PLAYER.x * constants.CELL_WIDTH + constants.CELL_WIDTH / 2
        target_y = globals.PLAYER.y * constants.CELL_HEIGHT + constants.CELL_HEIGHT / 2

        distance_x, distance_y = self.map_distance((target_x, target_y))

        self.x += int(distance_x)
        self.y += int(distance_y)

    def window_to_map(self, coordinates):

        # convert coordinates to distance from camera
        x_distance, y_distance = self.camera_distance(coordinates)

        # convert distance from camera to a map pixel coordinate
        map_x = self.x + x_distance
        map_y = self.y + y_distance

        return map_x, map_y

    def camera_distance(self, coordinates):

        window_x, window_y = coordinates
        distance_x = window_x - self.width / 2
        distance_y = window_y - self.height / 2

        return distance_x, distance_y

    def map_distance(self, coordinates):

        map_x, map_y = coordinates

        dist_x = map_x - self.x
        dist_y = map_y - self.y

        return dist_x, dist_y
