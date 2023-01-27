import arcade

from copy import copy
from dataclasses import dataclass, make_dataclass
from itertools import product

from tile import *

@dataclass
class SpriteAggregate:
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
    def __init__(self):
        self.sprites_at = dict()
        self.new_sprites_at = dict()
        self.indices_for_coords = dict()
        self.sprite_lists = [arcade.SpriteList() for _ in SPRITE_SCALES]
        self.cursor_tile_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_overlay_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_coords = Coords(0, 0)
        self.tied_to_cursor = None

    def setup(self, tiles):
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
        
        def remove_in_all_scales(sprites):
            print(sprites)
            if sprites is None: return
            for i in range(len(SPRITE_SCALES)):
                self.sprite_lists[i].remove(sprites[i])

        for coords in self.new_sprites_at:
            print(coords, self.sprites_at[coords].projection,
                  self.new_sprites_at[coords].projection)
            index = self.sprite_lists[0].index(self.sprites_at[coords].tile[0])

            remove_in_all_scales(self.sprites_at[coords].tile)
            remove_in_all_scales(self.sprites_at[coords].projection)
            remove_in_all_scales(self.sprites_at[coords].building)
            remove_in_all_scales(self.sprites_at[coords].cursor)
            remove_in_all_scales(self.sprites_at[coords].icon)

            self.sprites_at[coords] = self.new_sprites_at[coords]
            
            for i in range(len(SPRITE_SCALES)):
                sprite_aggregate = self.sprites_at[coords]
                if sprite_aggregate.icon is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.icon[i])
                if sprite_aggregate.cursor is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.cursor[i])
                if sprite_aggregate.building is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.building[i])
                if sprite_aggregate.projection is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.projection[i])
                if sprite_aggregate.tile is not None:
                    self.sprite_lists[i].insert(index, sprite_aggregate.tile[i])
        self.new_sprites_at.clear()

    def update_layer_at(self, coords: Coords, layer, sprites):
        assert coords in self.sprites_at
        assert len(sprites) == len(SPRITE_SCALES)

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

    def apply_changes(self, layer, shape, erase=False):
        if shape is None: return

        for rel_coords, sprites in shape.items():
            abs_coords = self.cursor_coords + rel_coords
            if abs_coords not in self.sprites_at: continue
            if erase: self.update_layer_at(abs_coords, layer, None)
            else: self.update_layer_at(abs_coords, layer, sprites)

    def move_cursor(self, direction: int):
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

        self.update_layer_at(previous_coords, 'cursor', self.cursor_tile_sprites)
        self.update_layer_at(self.cursor_coords, 'cursor', self.cursor_tile_sprites)
        self.update_tied_to_cursor(previous_coords, True)
        self.update_tied_to_cursor(self.cursor_coords, False)

    def update_tied_to_cursor(self, coords, erase=False):
        if self.tied_to_cursor is not None:
            print('I updated!:', erase)
            self.apply_changes('projection', self.tied_to_cursor(coords), erase)

    def tie_to_cursor(self, action):
        self.tied_to_cursor = action
        self.update_tied_to_cursor(self.cursor_coords, False)

    def untie_from_cursor(self):
        self.tied_to_cursor = None
        self.update_tied_to_cursor(self.cursor_coords)

    def draw(self, scale_index):
        self.sprite_lists[scale_index].draw()
        self.cursor_overlay_sprites[scale_index].draw()
        
