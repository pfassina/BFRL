# modules
import random
import tcod

# game files
from bfrl import constants
from bfrl import data
from bfrl import generator
from bfrl import globals


class GameMap:

    def __init__(self, map_width, map_height):

        self.map_width = map_width
        self.map_height = map_height

        self.map_tiles = [
            [data.Tile(True) for _ in range(0, constants.MAP_HEIGHT)] for _ in range(0, constants.MAP_WIDTH)
        ]

        self.list_of_rooms = []
        self.list_of_objects = []

    def generate_dungeon(self, number_of_rooms, room_min_width, room_max_width, room_min_height, room_max_height):

        for room in range(number_of_rooms):

            w = tcod.random_get_int(None, room_min_width, room_max_width)
            h = tcod.random_get_int(None, room_min_height, room_max_height)

            x = tcod.random_get_int(None, 2, self.map_width - w - 2)
            y = tcod.random_get_int(None, 2, self.map_height - h - 2)

            new_room = ObjectRoom((x, y), (w, h))

            # Check for interference
            failed = False
            for other_room in self.list_of_rooms:
                if new_room.intercept(other_room):
                    failed = True

            # Place the room
            if not failed:
                self.create_room(new_room)
                if len(self.list_of_rooms) != 0:
                    other_room = self.list_of_rooms[-1]
                    self.create_tunnel(new_room.center, other_room.center)

                self.list_of_rooms.append(new_room)

        self.assign_tiles()
        make_fov(self.map_tiles)
        self.place_objects()

    def create_room(self, new_room):
        for x in range(new_room.x1, new_room.x2):
            for y in range(new_room.y1, new_room.y2):
                self.map_tiles[x][y].block_path = False

    def create_tunnel(self, room1, room2):

        x1, y1 = room1
        x2, y2 = room2

        if random.choice([True, False]):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.map_tiles[x][y1].block_path = False
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.map_tiles[x2][y].block_path = False
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.map_tiles[x1][y].block_path = False
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.map_tiles[x][y2].block_path = False

    def check_for_wall(self, x, y):
        """
        Checks if tile is wall
        :param x: tile x coordinate
        :param y: tile y coordinate
        :return: True if wall
        """

        try:
            return self.map_tiles[x][y].block_path
        except IndexError:
            return True

    def assign_tiles(self):

        for x in range(len(self.map_tiles)):
            for y in range(len(self.map_tiles[0])):

                if self.check_for_wall(x, y):

                    pos_w = self.check_for_wall(x - 1, y)
                    pos_e = self.check_for_wall(x + 1, y)
                    pos_n = self.check_for_wall(x, y + 1)
                    pos_s = self.check_for_wall(x, y - 1)
                    pos_nw = self.check_for_wall(x - 1, y - 1)
                    pos_sw = self.check_for_wall(x - 1, y + 1)
                    pos_ne = self.check_for_wall(x + 1, y - 1)
                    pos_se = self.check_for_wall(x + 1, y + 1)

                    if pos_w & pos_e & pos_n & pos_s & pos_nw & pos_sw & pos_ne & pos_se:
                        self.map_tiles[x][y].assignment = 998
                    else:
                        self.map_tiles[x][y].assignment = 0

                else:
                    self.map_tiles[x][y].assignment = 999

        for x in range(len(self.map_tiles)):
            for y in range(len(self.map_tiles[0])):

                if self.map_tiles[x][y].assignment == 0:

                    tile_assignment = 0
                    if y - 1 >= 0:
                        if self.map_tiles[x][y - 1].assignment <= 99:
                            tile_assignment += 1
                    if x + 1 < len(self.map_tiles):
                        if self.map_tiles[x + 1][y].assignment <= 99:
                            tile_assignment += 2
                    if y + 1 < len(self.map_tiles[0]):
                        if self.map_tiles[x][y + 1].assignment <= 99:
                            tile_assignment += 4
                    if x - 1 >= 0:
                        if self.map_tiles[x - 1][y].assignment <= 99:
                            tile_assignment += 8

                    self.map_tiles[x][y].assignment = tile_assignment

    def place_objects(self):

        current_level = len(globals.GAME.maps_previous) + 1
        first_level = (current_level == 1)
        final_level = (current_level == constants.MAP_LEVELS)

        rooms = len(self.list_of_rooms) - 1
        for room_number, room in enumerate(self.list_of_rooms):
            if room_number == 0:
                globals.PLAYER.x, globals.PLAYER.y = room.center
                if first_level:
                    generator.portal(room.center)
                else:
                    generator.stairs(room.center, downwards=False)
                continue
            elif room_number == rooms:
                if final_level:
                    generator.lamp(room.center)
                else:
                    generator.stairs(room.center)

            # Place a random enemy
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            generator.enemy((x, y))

            # Place a random item
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            generator.item((x, y))

    def check_for_creature(self, x, y, exclude_object=None):
        """
        Check for creature on target tile. Returns creature owner if found.
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param exclude_object: whether an object should be ignored from check.
        :return: creature owner object on tile. None if no creature on tile.
        """

        target = None
        if exclude_object:
            for obj in self.list_of_objects:
                if obj is not exclude_object and obj.x == x and obj.y == y and obj.creature:
                    target = obj
        else:
            for obj in globals.GAME.objects_on_map:
                if obj.x == x and obj.y == y and obj.creature:
                    target = obj

        return target


class ObjectRoom:
    """
    This is a rectangle room that lives on the map.
    """

    def __init__(self, coordinates, size):

        self.x1, self.y1 = coordinates
        self.w, self.h = size
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

    @property
    def center(self):
        center_x = int((self.x1 + self.x2)/2)
        center_y = int((self.y1 + self.y2)/2)
        return center_x, center_y

    def intercept(self, other):

        x_overlap = self.x1 <= other.x2 and self.x2 >= other.x1
        y_overlap = self.y1 <= other.y2 and self.y2 >= other.y1
        return x_overlap and y_overlap


class Node:

    def __init__(self, parent=None, position=None):
        """
        A node class for the A* Pathfinding algorithm.

        f, g, and h are variables of the Node Class.
        g: Distance between the current node and start node (G)
        g: Estimated distance from the current node to the end node
        f: Total Cost of the Node

        f = g + h

        :param parent: parent node
        :param position: node position on the map
        """

        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def make_fov(incoming_map):

    globals.FOV_MAP = tcod.map.Map(constants.MAP_WIDTH, constants.MAP_HEIGHT)

    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
            if incoming_map[x][y].block_path:
                globals.FOV_MAP.transparent[y, x] = False
                globals.FOV_MAP.walkable[y, x] = False
            else:
                globals.FOV_MAP.transparent[y, x] = True
                globals.FOV_MAP.walkable[y, x] = True


def calculate_fov():

    if globals.FOV_CALCULATE:
        globals.FOV_CALCULATE = False
        globals.FOV_MAP.compute_fov(globals.PLAYER.x, globals.PLAYER.y, constants.TORCH_RADIUS,
                                    constants.FOV_LIGHT_WALLS, constants.FOV_ALGORITHM)


def objects_at_coordinates(x, y):

    object_options = [obj for obj in globals.GAME.objects_on_map if obj.x == x and obj.y == y]
    return object_options


def find_line(origin_coordinates, destination_coordinates):
    """
    Converts two coordinates into a list of titles.
    :param origin_coordinates: (x1, y1)
    :param destination_coordinates: (x2, y2)
    :return: list of coordinates between coordinates 1 and coordinates 2.
    """

    x1, y1 = origin_coordinates
    x2, y2 = destination_coordinates

    coordinate_list = list(tcod.line_iter(x1, y1, x2, y2))
    return coordinate_list


def find_radius(coordinates, radius):
    """
    Returns all tiles within a radius of a center tile
    :param coordinates: center tile (x, y) tuple
    :param radius: radius length
    :return: list of tiles within radius of center tile
    """

    center_x, center_y = coordinates
    tile_list = []
    for x in range(center_x - radius, center_x + radius + 1):
        for y in range(center_y - radius, center_y + radius + 1):
            tile_list.append((x, y))

    return tile_list
