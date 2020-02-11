# modules
import random
import tcod

# game files
from bfrl import constants
from bfrl import data
from bfrl import generator
from bfrl import globals


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


def create():

    # Create a map of Height by Width dimensions
    new_map = [[data.Tile(True) for _ in range(0, constants.MAP_HEIGHT)] for _ in range(0, constants.MAP_WIDTH)]

    # Generate new room
    list_of_rooms = []
    for room in range(constants.MAP_MAX_NUM_ROOMS):

        w = tcod.random_get_int(None, constants.ROOM_MIN_WIDTH, constants.ROOM_MAX_WIDTH)
        h = tcod.random_get_int(None, constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT)

        x = tcod.random_get_int(None, 2, constants.MAP_WIDTH - w - 2)
        y = tcod.random_get_int(None, 2, constants.MAP_HEIGHT - h - 2)

        new_room = ObjectRoom((x, y), (w, h))

        # Check for interference
        failed = False
        for other_room in list_of_rooms:
            if new_room.intercept(other_room):
                failed = True

        # Place the room
        if not failed:
            create_room(new_map, new_room)
            if len(list_of_rooms) != 0:
                other_room = list_of_rooms[-1]
                create_tunnel(new_map, new_room.center, other_room.center)

            list_of_rooms.append(new_room)

    assign_tiles(new_map)
    make_fov(new_map)

    return new_map, list_of_rooms


def create_room(new_map, room):
    for x in range(room.x1, room.x2):
        for y in range(room.y1, room.y2):
            new_map[x][y].block_path = False


def create_tunnel(new_map, room1, room2):

    x1, y1 = room1
    x2, y2 = room2

    if random.choice([True, False]):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y1].block_path = False
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[x2][y].block_path = False
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[x1][y].block_path = False
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y2].block_path = False


def assign_tiles(tile_map):

    for x in range(len(tile_map)):
        for y in range(len(tile_map[0])):

            tile_assignment = 0
            tile_is_wall = check_for_wall(tile_map, x, y)
            if tile_is_wall:
                if check_for_wall(tile_map, x, y - 1):
                    tile_assignment += 1
                if check_for_wall(tile_map, x + 1, y):
                    tile_assignment += 2
                if check_for_wall(tile_map, x, y + 1):
                    tile_assignment += 4
                if check_for_wall(tile_map, x - 1, y):
                    tile_assignment += 8

            tile_map[x][y].assignment = tile_assignment


def place_objects(room_list):

    current_level = len(globals.GAME.maps_previous) + 1
    first_level = (current_level == 1)
    final_level = (current_level == constants.MAP_LEVELS)

    rooms = len(room_list) - 1
    for room_number, room in enumerate(room_list):
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


def check_for_creature(x, y, exclude_object=None):
    """
    Check for creature on target tile. Returns creature owner if found.
    :param x: tile x coordinate
    :param y: tile y coordinate
    :param exclude_object: whether an object should be ignored from check.
    :return: creature owner object on tile. None if no creature on tile.
    """

    target = None
    if exclude_object:
        for obj in globals.GAME.current_objects:
            if obj is not exclude_object and obj.x == x and obj.y == y and obj.creature:
                target = obj
    else:
        for obj in globals.GAME.current_objects:
            if obj.x == x and obj.y == y and obj.creature:
                target = obj

    return target


def check_for_wall(incoming_map, x, y):
    """
    Checks if tile is wall
    :param incoming_map: reference map
    :param x: tile x coordinate
    :param y: tile y coordinate
    :return: True if wall
    """

    try:
        return incoming_map[x][y].block_path
    except IndexError:
        return False




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

    object_options = [obj for obj in globals.GAME.current_objects if obj.x == x and obj.y == y]
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
