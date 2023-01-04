# standard libraries
import pygame

# game files
from bfrl import constants
from bfrl import globals


class UIButton:

    def __init__(self, size, surface, center_coordinates, button_text,
                 color_box_default=constants.COLOR_RED,
                 color_box_mouse_over=constants.COLOR_GREEN,
                 color_text_default=constants.COLOR_BLACK,
                 color_text_mouse_over=constants.COLOR_WHITE
                 ):

        self.size = size
        self.surface = surface
        self.center_coordinates = center_coordinates
        self.button_text = button_text

        self.color_box_default = color_box_default
        self.color_box_mouse_over = color_box_mouse_over
        self.color_text_default = color_text_default
        self.color_text_mouse_over = color_text_mouse_over

        self.current_box_color = self.color_box_default
        self.current_text_color = self.color_text_default

        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = self.center_coordinates

    def update(self, player_input):

        local_events, local_mouse_position = player_input
        mouse_x, mouse_y = local_mouse_position

        mouse_clicked = False
        mouse_over = False

        if self.rect.left <= mouse_x <= self.rect.right and self.rect.bottom >= mouse_y >= self.rect.top:
            mouse_over = True

        for event in local_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        if mouse_over:
            self.current_box_color = self.color_box_mouse_over
            self.current_text_color = self.color_text_mouse_over

        else:
            self.current_box_color = self.color_box_default
            self.current_text_color = self.color_text_default

        if mouse_over and mouse_clicked:
            return True

    def draw(self):
        pygame.draw.rect(self.surface, self.current_box_color, self.rect)
        text(display_surface=self.surface, text_to_display=self.button_text,
             font=constants.FONT_DEBUG_MESSAGE, coordinates=self.center_coordinates,
             text_color=self.current_text_color, alignment='center')


class UISlider:

    def __init__(self, size, surface, center_coordinates, color_background, color_foreground, value):

        self.size = size
        self.surface = surface
        self.center_coordinates = center_coordinates
        self.color_background = color_background
        self.color_foreground = color_foreground
        self.value = value

        self.bg_rect = pygame.Rect((0, 0), self.size)
        self.bg_rect.center = self.center_coordinates

        self.fg_rect = pygame.Rect((0, 0), (self.bg_rect.width * self.value, self.bg_rect.height))
        self.fg_rect.topleft = self.bg_rect.topleft

        self.grip_rect = pygame.Rect((0, 0), (10, self.bg_rect.height + 8))
        self.grip_rect.center = self.fg_rect.midright

    def update(self, player_input):

        local_events, local_mouse_position = player_input
        mouse_x, mouse_y = local_mouse_position

        mouse_over = False
        if self.bg_rect.left <= mouse_x <= self.bg_rect.right and self.bg_rect.bottom >= mouse_y >= self.bg_rect.top:
            mouse_over = True

        mouse_down = pygame.mouse.get_pressed()[0]
        if mouse_over and mouse_down:

            # update value with mouse relative position
            self.value = (mouse_x - self.bg_rect.left) / self.bg_rect.width

            # update foreground rectangle based on new value
            self.fg_rect.width = self.bg_rect.width * self.value
            self.grip_rect.center = self.fg_rect.midright

    def draw(self):

        # draw background rectangle
        pygame.draw.rect(self.surface, self.color_background, self.bg_rect)

        # drag foreground rectangle
        pygame.draw.rect(self.surface, self.color_foreground, self.fg_rect)

        # drag foreground rectangle
        pygame.draw.rect(self.surface, constants.COLOR_RED, self.grip_rect)


def game():

    # global SURFACE_MAIN

    # clear the surface
    globals.SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    globals.SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

    globals.CAMERA.update()

    # draw the map
    map_surface(globals.GAME.current_map.map_tiles)

    # draw the characters
    for obj in sorted(globals.GAME.objects_on_map, key=(lambda x: x.depth), reverse=True):
        obj.draw()

    globals.SURFACE_MAIN.blit(globals.SURFACE_MAP, (0, 0), globals.CAMERA.rectangle)

    debug()
    messages()


def map_surface(map_to_draw):

    camera_x, camera_y = globals.CAMERA.map_address
    display_map_width = constants.CAMERA_WIDTH / constants.CELL_WIDTH
    display_map_height = constants.CAMERA_HEIGHT / constants.CELL_HEIGHT

    # Define Dimensions of the map to be drawn
    render_width_min = max(int(camera_x - display_map_width / 2), 0)
    render_width_max = min(int(camera_x + display_map_width / 2), constants.MAP_WIDTH)

    render_height_min = max(int(camera_y - display_map_height / 2), 0)
    render_height_max = min(int(camera_y + display_map_height / 2), constants.MAP_HEIGHT)

    walls = globals.ASSETS.sprite('walls')

    for x in range(render_width_min, render_width_max):
        for y in range(render_height_min, render_height_max):

            x_cell = x * constants.CELL_WIDTH
            y_cell = y * constants.CELL_HEIGHT

            is_visible = globals.FOV_MAP.fov[y, x]
            if is_visible:
                map_to_draw[x][y].explored = True
                if map_to_draw[x][y].block_path:
                    facing = map_to_draw[x][y].assignment
                    globals.SURFACE_MAP.blit(walls['default'][facing], (x_cell, y_cell))
                else:
                    globals.SURFACE_MAP.blit(globals.ASSETS.sprite('S_FLOOR'), (x_cell, y_cell))

            elif map_to_draw[x][y].explored:
                if map_to_draw[x][y].block_path:
                    facing = map_to_draw[x][y].assignment
                    globals.SURFACE_MAP.blit(walls['explored'][facing], (x_cell, y_cell))
                else:
                    globals.SURFACE_MAP.blit(globals.ASSETS.sprite('S_FLOOR_EXPLORED'), (x_cell, y_cell))


def debug():
    debug_message = f'FPS: {int(globals.CLOCK.get_fps())}'
    font_color = constants.COLOR_WHITE
    bg_color = constants.COLOR_BLACK
    text(globals.SURFACE_MAIN, debug_message, constants.FONT_DEBUG_MESSAGE, (0, 0), font_color, bg_color)


def messages():

    if len(globals.GAME.message_history) <= constants.NUM_MESSAGES:
        to_draw = globals.GAME.message_history
    else:
        to_draw = globals.GAME.message_history[-constants.NUM_MESSAGES:]

    text_height = helper_text_height(constants.FONT_MESSAGE_TEXT)

    start_y = constants.CAMERA_HEIGHT - (constants.NUM_MESSAGES * text_height) - 10

    for index, (message, color) in enumerate(to_draw):
        message_location = (0, start_y + index * text_height)
        text(globals.SURFACE_MAIN, message, constants.FONT_MESSAGE_TEXT, message_location, color, constants.COLOR_BLACK)


def text(display_surface, text_to_display, font, coordinates, text_color, back_color=None, alignment='top-left'):

    """
    This function takes in some text, and display it on the referenced surfaced
    :param alignment:
    :param display_surface: Surface to display text
    :param text_to_display: Text to be displayed
    :param font: font of the text
    :param coordinates: Coordinates tuple
    :param text_color: Text color
    :param back_color: Text background color
    """

    text_surface, text_rectangle = helper_text_objects(text_to_display, font, text_color, back_color)

    if alignment == 'top-left':
        text_rectangle.topleft = coordinates
    elif alignment == 'center':
        text_rectangle.center = coordinates
    else:
        text_rectangle.topleft = coordinates

    display_surface.blit(text_surface, text_rectangle)


def tile_rect(coordinates, tile_color=None, tile_alpha=150, marker=None):

    x, y = coordinates
    new_x = x * constants.CELL_WIDTH
    new_y = y * constants.CELL_HEIGHT

    if tile_color:
        local_color = tile_color
    else:
        local_color = constants.COLOR_WHITE

    new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
    new_surface.fill(local_color)
    new_surface.set_alpha(tile_alpha)

    if marker:
        mx = int(round(constants.CELL_WIDTH / 2))
        my = int(round(constants.CELL_HEIGHT / 2))
        marker_font = constants.FONT_CURSOR_TEXT
        marker_color = constants.COLOR_BLACK
        align = 'center'
        text(new_surface, marker, font=marker_font, coordinates=(mx, my), text_color=marker_color, alignment=align)

    # SURFACE_MAIN
    globals.SURFACE_MAP.blit(new_surface, (new_x, new_y))


def helper_text_objects(incoming_text, incoming_font, incoming_color, incoming_background):

    if incoming_background:
        text_surface = incoming_font.render(incoming_text, False, incoming_color, incoming_background)
    else:
        text_surface = incoming_font.render(incoming_text, False, incoming_color)

    return text_surface, text_surface.get_rect()


def helper_text_height(font):
    """
    Returns the Height of a font in pixels
    :param font: font to be examined
    :return: font height in pixels
    """

    font_object = font.render('a', False, (0, 0, 0))
    font_rect = font_object.get_rect()

    return font_rect.height


def helper_text_width(font):
    """
    Returns the width of a font in pixels
    :param font: font to be examined
    :return: font height in pixels
    """

    font_object = font.render('a', False, (0, 0, 0))
    font_rect = font_object.get_rect()

    return font_rect.width
