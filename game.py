import arcade
from pyglet.math import Vec2

import random

from tile import *
from building import *
from generator import *


RESOLUTION = (1200, 800)
SCREEN_TITLE = 'Terraform'
PATH_TO_ASSETS = 'assets/'
CAMERA_SPEED = 10
CAMERA_ZOOM = 0.1


class Game(arcade.Window):
    def __init__(self, resolution, title):
        super().__init__(resolution[0], resolution[1], title)

        self.tile_sprites = [None] * len(SPRITE_SCALES)
        self.cursor_front_sprite = None
        self.cursor_back_sprite = None
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.num_add_pressed = False
        self.num_subtract_pressed = False

        self.camera = arcade.Camera(RESOLUTION[0], RESOLUTION[1])
        self.camera_position = [0, 0]
        self.scale = 2

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

        self.cursor_front_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor_front.png', scale)
                                     for scale in SPRITE_SCALES]
        self.cursor_back_sprites = [arcade.Sprite(PATH_TO_ASSETS+'cursor_back.png', scale)
                                    for scale in SPRITE_SCALES]

    def on_draw(self):
        self.clear()

        self.camera.use()
        
        self.tile_sprites[self.scale].draw()
        
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
