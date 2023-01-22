import arcade
from pyglet.math import Vec2

import random

from tile import *
from building import *
from generator import *


RESOLUTION = (1920, 1080)
SCREEN_TITLE = 'Terraform'
PATH_TO_ASSETS = 'assets/'
CAMERA_SPEED = 10
CAMERA_ZOOM = 0.1


class Game(arcade.Window):
    def __init__(self, resolution, title):
        super().__init__(resolution[0], resolution[1], title)

        self.tile_sprites = None
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.num_add_pressed = False
        self.num_subtract_pressed = False

        self.camera = arcade.Camera(RESOLUTION[0], RESOLUTION[1])
        self.camera_position = [0, 0]
        self.camera_zoom = 1

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

        self.world_generator = StandardGenerator(213702, self.terrain_types)
        self.tiles = self.world_generator()
        #self.tiles = [Tile(Coords(0, 0), self.terrain_types['rocky'], 0),
        #              Tile(direction(0), self.terrain_types['rough'], 0),
        #              Tile(direction(2), self.terrain_types['sand'], 0),
        #              Tile(direction(4), self.terrain_types['soil'], 0)]
        self.tile_sprites = arcade.SpriteList()
        for tile in sorted(self.tiles.values(), key=lambda t: t.coords.priority()):
            self.tile_sprites.append(tile.sprite)

    def on_draw(self):
        self.clear()

        self.camera.use()
        
        self.tile_sprites.draw()
        
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
        elif key == arcade.key.NUM_ADD:
            self.num_add_pressed = True
        elif key == arcade.key.NUM_SUBTRACT:
            self.num_subtract_pressed = True

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
            self.num_add_pressed = False
        elif key == arcade.key.NUM_SUBTRACT:
            self.num_subtract_pressed = False

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
        #if self.num_add_pressed and not self.num_subtract_pressed:
        #    self.camera_zoom = min(self.camera_zoom*(1+CAMERA_ZOOM), 10)
        #elif self.num_subtract_pressed and not self.num_add_pressed:
        #    self.camera_zoom = max(self.camera_zoom/(1+CAMERA_ZOOM), 0.1)
            
        position = Vec2(self.camera_position[0] - self.width / 2,
                        self.camera_position[1] - self.height / 2)
        
        self.camera.move_to(position, 1)

        #self.camera.resize(RESOLUTION[0] * self.camera_zoom, RESOLUTION[1] * self.camera_zoom)

def main():
    game = Game(RESOLUTION, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == '__main__':
    main()
