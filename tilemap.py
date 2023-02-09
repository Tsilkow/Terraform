import arcade

from copy import copy
from dataclasses import dataclass, make_dataclass
from itertools import product

from tile import *


SPRITE_LAYERS = [
    'tile', 'ore', 'projection',
    'tunnels_singular', 'tunnels_0', 'tunnels_1', 'tunnels_5', 'tunnels_2', 'tunnels_4', 'tunnels_3',
    'pipes_singular', 'pipes_0', 'pipes_1', 'pipes_5', 'pipes_2', 'pipes_4', 'pipes_3',
    'wires_singular', 'wires_0', 'wires_1', 'wires_5', 'wires_2', 'wires_4', 'wires_3',
    'building', 'cursor', 'icon']


class SpriteAggregate(dict):
    """
    Dict subclass for storing layers of sprites (and their scaled versions) 
    tied to a particular location. 
    :tile: layer for terrain sprites
    :ore: layer for ores and underground water deposits
    :projection: layer for terrain changes projections, including terraforms
    :ore_projection: layer for ore changes projections
    :tunnel_singular:
    :tunnel_0:
    :tunnel_1:
    :tunnel_5:
    :tunnel_2:
    :tunnel_4:
    :tunnel_3:
    :pipes_singular:
    :pipes_0:
    :pipes_1:
    :pipes_5:
    :pipes_2:
    :pipes_4:
    :pipes_3:
    :wires_singular:
    :wires_0:
    :wires_1:
    :wires_5:
    :wires_2:
    :wires_4:
    :wires_3:
    :building: layer for building sprites
    :cursor: layer for tilemap cursor sprite
    :icon: layer for special icons
    """
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __copy__(self):
        copied = SpriteAggregate()
        for layer in SPRITE_LAYERS:
            if layer in self:
                copied[layer] = [*self[layer]]

        return copied


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
            self.sprites_at[tile.coords] = SpriteAggregate({'tile': tile.terrain_sprites})
            for scale_index in range(len(SPRITE_SCALES)):
                self.sprite_lists[scale_index].append(tile.terrain_sprites[scale_index])
                
        for tile in sorted(tiles.values(), key=lambda t: t.coords.priority()):
            for i, sprites in enumerate(tile.tunnel_sprites):
                if sprites is None: continue
                if i == 0: self._set_sprite_at(tile.coords, 'tunnels_singular', sprites)
                else: self._set_sprite_at(tile.coords, f'tunnels_{i-1}', sprites)

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
        self._set_sprite_at(self.cursor_coords, 'cursor', self.cursor_tile_sprites)

    def update(self):
        """
        Method for applying changes in sprite position and configurations
        declared. Should be called every frame.
        """
        
        def remove_in_all_scales(aggregate):
            for sprites in aggregate.values():
                if sprites is None: return
                for i in range(len(SPRITE_SCALES)):
                    self.sprite_lists[i].remove(sprites[i])

        def insert_in_all_scales(aggregate, index):
            for sprites in reversed(aggregate.values()):
                if sprites is None: return
                for i in range(len(SPRITE_SCALES)):
                    self.sprite_lists[i].insert(index, sprites[i])

        for coords in self.new_sprites_at:
            index = self.sprite_lists[0].index(self.sprites_at[coords]['tile'][0])

            remove_in_all_scales(self.sprites_at[coords])
            
            self.sprites_at[coords] = self.new_sprites_at[coords]

            insert_in_all_scales(self.sprites_at[coords], index)
            
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

        if layer in SPRITE_LAYERS:
            if sprites is None: self.new_sprites_at[coords].pop(layer, None)
            else: self.new_sprites_at[coords][layer] = sprites
        else: raise ValueError('invalid layer', layer)

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
                self.sprites_at[self.cursor_coords]['tile'][scale_index].center_x,
                self.sprites_at[self.cursor_coords]['tile'][scale_index].center_y)
            cur_tile.center_x, cur_tile.center_y = new_cursor_center
            cur_over.center_x, cur_over.center_y = new_cursor_center

        self._set_sprite_at(previous_coords, 'cursor', None)
        self._set_sprite_at(self.cursor_coords, 'cursor', self.cursor_tile_sprites)
        self._update_tied_to_cursor(previous_coords, True)
        self._update_tied_to_cursor(self.cursor_coords, False)

        return True

    def get_cursor_position(self, scale_index):
        """
        Method for retrieving pixel position of center of cursor on the tilemap
        :scale_index: index of scale which use to retrive the center
        """
        return (self.cursor_overlay_sprites[scale_index].center_x,
                self.cursor_overlay_sprites[scale_index].center_y)

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
        
