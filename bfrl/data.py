
class Tile:
    """
    This class functions as a struct that tracks the data for each
    tile within a map.

    ** PROPERTIES **
    StructureTile.block_path : TRUE if tile prevents actors from moving through it under normal circumstances.
    StructureTile.explored : Initializes to FALSE, set to true if player has seen it before.
    """

    def __init__(self, block_path):
        self.block_path = block_path
        self.explored = False
        self.assignment = 0


class Preferences:

    def __init__(self):

        self.volume_sound = .5
        self.volume_music = .5
