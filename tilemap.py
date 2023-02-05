import arcade

from copy import copy
from dataclasses import dataclass, make_dataclass
from itertools import product

from tile import *

@dataclass
class SpriteAggregate:
    """
    Data class for storing layers of sprites (and their scaled versions) 
    tied to a particular location. 
    :tile: layer for terrain sprites
    :projection: layer for terrain changes projections, including terraforms
    :building: layer for building sprites
    :cursor: layer for tilemap cursor sprite
    :icon: layer for special icons
    """
    tile: list[arcade.Sprite]
    projection: list[arcade.Sprite]
    building: list[arcade.Sprite]
    cursor: list[arcade.Sprite]
    icon: list[arcade.Sprite]

    def __copy__(self):
        tmp_tile = [*self.tile] if self.tile is not None else None
        tmp_projection = [*self.projection] if self.projection is not None else None
        tmp_building = [*self.building] if self.building is not None else None
        tmp_cursor = [*self.cursor] if self.cursor is not None else None
        tmp_icon = [*self.icon] if self.icon is not None else None
        return SpriteAggregate(tmp_tile, tmp_projection, tmp_building, tmp_cursor, tmp_icon)


class Tilemap(object):
    """
    Tilemap stores tile sprites and all sprites displayed on the tilemap, 
    changes to said sprites, handles cursor and displaying everything tied
    to cursor position.
    """
    def __init__(self):
        self.sprites_at = dict()
        self.new_sprites_at = dict()
        self.sprite_lists = [arcade.SpriteList() for _ in SPRITE_SCALES]
        self.cursor_tile_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_overlay_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_coords = Coords(0, 0)
        self.tied_to_cursor = None

    def setup(self, tiles):
        """
        Total refresh of tilemap, resulting display is ground truth of what
        should or shouldn't be displayed.
        :tiles: tiles used to construct the tilemap
        """
        self.sprites_at = dict()
        self.new_sprites_at = dict()
        self.sprite_lists = [arcade.SpriteList() for _ in SPRITE_SCALES]
        for tile in sorted(tiles.values(), key=lambda t: t.coords.priority()):
            self.sprites_at[tile.coords] = SpriteAggregate(tile.sprites, None, None, None, None)
            for scale_index in range(len(SPRITE_SCALES)):
                self.sprite_lists[scale_index].append(tile.sprites[scale_index])

        self.cursor_tile_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor.png', scale)
                                    for scale in SPRITE_SCALES]
        self.cursor_overlay_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor.png', scale)
                                       for scale in SPRITE_SCALES]
        self.sprites_at[self.cursor_coords].cursor = self.cursor_tile_sprites
        for i, (cur_tile, cur_over) in enumerate(
                zip(self.cursor_tile_sprites, self.cursor_overlay_sprites)):
            cur_tile.center_x, cur_tile.center_y = tiles[self.cursor_coords].center_pixel(i)
            cur_over.center_x, cur_over.center_y = tiles[self.cursor_coords].center_pixel(i)
            cur_over.alpha = 128
            visited_sprite_index = self.sprite_lists[i].index(
                self.sprites_at[self.cursor_coords].tile[i])
            self.sprite_lists[i].insert(visited_sprite_index+1, cur_tile)

    def update(self):
        """
        Method for applying changes in sprite position and configurations
        declared. Should be called every frame.
        """
        
        def remove_in_all_scales(sprites):
            if sprites is None: return
            for i in range(len(SPRITE_SCALES)):
                self.sprite_lists[i].remove(sprites[i])

        for coords in self.new_sprites_at:
            index = self.sprite_lists[0].index(self.sprites_at[coords].tile[0])

            remove_in_all_scales(self.sprites_at[coords].tile)
            remove_in_all_scales(self.sprites_at[coords].projection)
            remove_in_all_scales(self.sprites_at[coords].building)
            remove_in_all_scales(self.sprites_at[coords].cursor)
            remove_in_all_scales(self.sprites_at[coords].icon)
            
            self.sprites_at[coords] = self.new_sprites_at[coords]
            sprite_aggregate = self.sprites_at[coords]
            projection_here = False
            for i in range(len(SPRITE_SCALES)):
                if sprite_aggregate.icon is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.icon[i])
                if sprite_aggregate.cursor is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.cursor[i])
                if sprite_aggregate.building is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.building[i])
                if sprite_aggregate.projection is not None:
                    projection_here = True
                    sprite_aggregate.projection[i].color = (255, 255, 255)
                    self.sprite_lists[i].insert(index, sprite_aggregate.projection[i])
                if sprite_aggregate.tile is not None:
                    sprite_aggregate.tile[i].visible = not projection_here
                    self.sprite_lists[i].insert(index, sprite_aggregate.tile[i])
        self.new_sprites_at.clear()

    def _set_sprite_at(self, coords: Coords, layer, sprites):
        """
        Internal method for placing new sprite at a specific position and layer.
        :coords: target coordinates
        :layer: target layer
        :sprites: sprite and its scaled versions to set
        """
        assert coords in self.sprites_at
        assert sprites is None or len(sprites) == len(SPRITE_SCALES)

        if coords not in self.new_sprites_at:
            self.new_sprites_at[coords] = copy(self.sprites_at[coords])
            
        if layer == 'tile':
            self.new_sprites_at[coords].tile = sprites
        elif layer == 'projection':
            self.new_sprites_at[coords].projection = sprites
        elif layer == 'building':
            self.new_sprites_at[coords].building = sprites
        elif layer == 'cursor':
            self.new_sprites_at[coords].cursor = sprites
        elif layer == 'icon':
            self.new_sprites_at[coords].icon = sprites
        else:
            raise ValueError('invalid layer')

    def _set_sprite_at_shape(self, shape, erase=False):
        """
        Internal method for placing multiple new sprites at a specific positions and layers.
        :shape: dictionary with target coordinates as keys and sprites to set as values
        :erase: flag for erasing instead of changing sprites at 
            given coordinates and layer; defaults to False
        """
        if shape is None: return

        for coords, layer, sprites in shape:
            if coords not in self.sprites_at: continue
            if erase: self._set_sprite_at(coords, layer, None)
            else: self._set_sprite_at(coords, layer, sprites)

    def move_cursor(self, direction: int):
        """
        Method for moving the cursor.
        :direction: direction of movement
        :return: True if move was performed, False otherwise
        """
        if self.cursor_coords.neighbour(direction) not in self.sprites_at: return False
        previous_coords = self.cursor_coords
        self.cursor_coords = self.cursor_coords.neighbour(direction)
        for scale_index, (cur_tile, cur_over) in enumerate(
                zip(self.cursor_tile_sprites, self.cursor_overlay_sprites)):
            new_cursor_center = (
                self.sprites_at[self.cursor_coords].tile[scale_index].center_x,
                self.sprites_at[self.cursor_coords].tile[scale_index].center_y)
            cur_tile.center_x, cur_tile.center_y = new_cursor_center
            cur_over.center_x, cur_over.center_y = new_cursor_center

        self._set_sprite_at(previous_coords, 'cursor', None)
        self._set_sprite_at(self.cursor_coords, 'cursor', self.cursor_tile_sprites)
        self._update_tied_to_cursor(previous_coords, True)
        self._update_tied_to_cursor(self.cursor_coords, False)

        return True

    def _update_tied_to_cursor(self, coords, erase=False):
        """
        Internal method for updating function tied to cursor position
        :coords: target coordinates to pass further
        :erase: flag for erasing output at previous coordinates; defaults to False
        """
        if self.tied_to_cursor is not None:
            self._set_sprite_at_shape(self.tied_to_cursor(coords), erase)

    def tie_to_cursor(self, action):
        """
        Method for setting a function that will be called after every cursor move
        :action: function to set
        """
        self.untie_from_cursor()
        self.tied_to_cursor = action
        self._update_tied_to_cursor(self.cursor_coords, False)

    def untie_from_cursor(self):
        """Method for removing function set to follow the cursor"""
        if self.tied_to_cursor is None: return
        self._update_tied_to_cursor(self.cursor_coords, True)
        self.tied_to_cursor = None

    def draw(self, scale_index):
        """Function for drawing the tilemap"""
        self.sprite_lists[scale_index].draw()
        self.cursor_overlay_sprites[scale_index].draw()
        
