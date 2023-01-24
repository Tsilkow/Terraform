import arcade
from pyglet.math import Vec2

import random

from coords import *
from tile import *
from building import *
from generator import *


RESOLUTION = (1200, 800)
SCREEN_TITLE = 'Terraform'
PATH_TO_ASSETS = 'assets/'
CAMERA_SPEED = 10
CURSOR_SPEED = 5


class Game(arcade.Window):
    def __init__(self, resolution, title):
        super().__init__(resolution[0], resolution[1], title)

        self.tile_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_tile_sprites = None
        self.cursor_overlay_sprites = None
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.num_add_pressed = False
        self.num_subtract_pressed = False
        self.q_pressed = False
        self.w_pressed = False
        self.e_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False

        self.camera = arcade.Camera(RESOLUTION[0], RESOLUTION[1])
        self.camera_position = [0, 0]
        self.scale = 2
        self.cursor_coords = Coords(0, 0)
        self.cursor_can_move = True
        self.cursor_timer = 0

        self.generator = None
        
    def setup(self):
        self.terrain_types = {
            'rocky': TerrainType('Rocky', PATH_TO_ASSETS+'terrain_rocky.png'),
            'rough': TerrainType('Rough', PATH_TO_ASSETS+'terrain_rough.png'),
            'sand' : TerrainType('Sand' , PATH_TO_ASSETS+'terrain_sand.png' ),
            'soil' : TerrainType('Soil' , PATH_TO_ASSETS+'terrain_soil.png' ),
            'water': TerrainType('Water', PATH_TO_ASSETS+'terrain_water.png'),
            'ice'  : TerrainType('Ice'  , PATH_TO_ASSETS+'terrain_ice.png'  )
            }

        self.world_generator = StandardGenerator(
            2137,
            self.terrain_types)
        self.tiles = self.world_generator()
        #self.tiles = [Tile(Coords(0, 0), self.terrain_types['rocky'], 0),
        #              Tile(direction(0), self.terrain_types['rough'], 0),
        #              Tile(direction(2), self.terrain_types['sand'], 0),
        #              Tile(direction(4), self.terrain_types['soil'], 0)]
        for i, scale in enumerate(SPRITE_SCALES):
            self.tile_sprites[i] = arcade.SpriteList()
            for tile in sorted(self.tiles.values(), key=lambda t: t.coords.priority()):
                self.tile_sprites[i].append(tile.sprites[i])

        self.cursor_tile_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor.png', scale)
                                    for scale in SPRITE_SCALES]
        self.cursor_overlay_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor.png', scale)
                                       for scale in SPRITE_SCALES]
        for i, (cur_tile, cur_over) in enumerate(
                zip(self.cursor_tile_sprites, self.cursor_overlay_sprites)):
            cur_tile.center_x, cur_tile.center_y = self.tiles[self.cursor_coords].center_pixel(i)
            cur_over.center_x, cur_over.center_y = self.tiles[self.cursor_coords].center_pixel(i)
            cur_over.alpha = 128
            visited_sprite_index = self.tile_sprites[i].index(
                self.tiles[self.cursor_coords].sprites[i])
            self.tile_sprites[i].insert(visited_sprite_index+1, cur_tile)

    def on_draw(self):
        self.clear()

        self.camera.use()
        
        self.tile_sprites[self.scale].draw()
        self.cursor_overlay_sprites[self.scale].draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.Q:
            self.q_pressed = True
        elif key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.E:
            self.e_pressed = True
        elif key == arcade.key.A:
            self.a_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True
        elif key == arcade.key.D:
            self.d_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.NUM_ADD:
            self.scale = min(self.scale+1, len(SPRITE_SCALES)-1)
        elif key == arcade.key.NUM_SUBTRACT:
            self.scale = max(self.scale-1, 0)
        elif key == arcade.key.Q:
            self.q_pressed = False
        elif key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.E:
            self.e_pressed = False
        elif key == arcade.key.A:
            self.a_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False
        elif key == arcade.key.D:
            self.d_pressed = False

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.up_pressed and not self.down_pressed:
            self.camera_position[1] += CAMERA_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.camera_position[1] += -CAMERA_SPEED
        if self.left_pressed and not self.right_pressed:
            self.camera_position[0] += -CAMERA_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.camera_position[0] += CAMERA_SPEED

        if self.cursor_can_move:
            if self.q_pressed and not self.d_pressed:
                self.update_cursor(5)
            elif self.d_pressed and not self.q_pressed:
                self.update_cursor(2)
            if self.w_pressed and not self.s_pressed:
                self.update_cursor(0)
            elif self.s_pressed and not self.w_pressed:
                self.update_cursor(3)
            if self.e_pressed and not self.a_pressed:
                self.update_cursor(1)
            elif self.a_pressed and not self.e_pressed:
                self.update_cursor(4)
        else:
            self.cursor_timer += 1
            if self.cursor_timer >= CURSOR_SPEED:
                self.cursor_can_move = True
                self.cursor_timer = 0
            
        position = Vec2(self.camera_position[0] - self.width / 2,
                        self.camera_position[1] - self.height / 2)
        
        self.camera.move_to(position, 1)

        #self.camera.resize(RESOLUTION[0] * self.camera_zoom, RESOLUTION[1] * self.camera_zoom)

    def update_cursor(self, direction: int):
        if self.cursor_coords.neighbour(direction) not in self.tiles: return
        self.cursor_coords = self.cursor_coords.neighbour(direction)
        self.cursor_can_move = False
        for i, (cur_tile, cur_over) in enumerate(
                zip(self.cursor_tile_sprites, self.cursor_overlay_sprites)):
            cur_tile.center_x, cur_tile.center_y = self.tiles[self.cursor_coords].center_pixel(i)
            cur_over.center_x, cur_over.center_y = self.tiles[self.cursor_coords].center_pixel(i)
            visited_sprite_index = self.tile_sprites[i].index(
                self.tiles[self.cursor_coords].sprites[i])
            self.tile_sprites[i].remove(cur_tile)
            self.tile_sprites[i].insert(visited_sprite_index+1, cur_tile)
            #self.tile_sprites[i].update()
        

def main():
    game = Game(RESOLUTION, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == '__main__':
    main()
