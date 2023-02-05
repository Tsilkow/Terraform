import arcade
from pyglet.math import Vec2

import random

from coords import *
from tile import *
from tilemap import *
from building import *
from generator import *


RESOLUTION = (1200, 800)
SCREEN_TITLE = 'Terraform'
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
        self.tilemap = None
        self.terraform = None
        
    def setup(self):
        self.world_generator = StandardGenerator(2137)
        self.tiles = self.world_generator()
        self.tilemap = Tilemap()
        self.tilemap.setup(self.tiles)
        #self.tiles = [Tile(Coords(0, 0), TERRAIN_TYPES['rocky'], 0),
        #              Tile(direction(0), TERRAIN_TYPES['rough'], 0),
        #              Tile(direction(2), TERRAIN_TYPES['sand'], 0),
        #              Tile(direction(4), TERRAIN_TYPES['soil'], 0)]

    def on_draw(self):
        self.clear()

        self.camera.use()

        self.tilemap.draw(self.scale)
        
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
        elif key == arcade.key.R:
            if self.terraform is not None:
                self.tilemap.untie_from_cursor()
                self.terraform.rotate(1)
                self.tilemap.tie_to_cursor(self.terraform.setup(self.tiles))
        elif key == arcade.key.T:
            self.terraform = Terraform()
            self.tilemap.tie_to_cursor(self.terraform.setup(self.tiles))
        elif key == arcade.key.Y and self.terraform is not None:
            self.tilemap.untie_from_cursor()
            self.terraform(self.tiles, self.tilemap.cursor_coords)
            self.tilemap.setup(self.tiles)
            self.terraform = None

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
                self.tilemap.move_cursor(5)
            elif self.d_pressed and not self.q_pressed:
                self.tilemap.move_cursor(2)
            if self.w_pressed and not self.s_pressed:
                self.tilemap.move_cursor(0)
            elif self.s_pressed and not self.w_pressed:
                self.tilemap.move_cursor(3)
            if self.e_pressed and not self.a_pressed:
                self.tilemap.move_cursor(1)
            elif self.a_pressed and not self.e_pressed:
                self.tilemap.move_cursor(4)
            self.cursor_can_move = False
        else:
            self.cursor_timer += 1
            if self.cursor_timer >= CURSOR_SPEED:
                self.cursor_can_move = True
                self.cursor_timer = 0
            
        position = Vec2(self.camera_position[0] - self.width / 2,
                        self.camera_position[1] - self.height / 2)
        
        self.camera.move_to(position, 1)

        self.tilemap.update()

        #self.camera.resize(RESOLUTION[0] * self.camera_zoom, RESOLUTION[1] * self.camera_zoom)
        

def main():
    game = Game(RESOLUTION, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == '__main__':
    main()
