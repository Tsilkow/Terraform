import arcade

from copy import copy
import random

from tile import *


class Terraform(object):
    operations = []
    
    def __init__(self):
        self.configuration = dict()
        self.sprites = [None] * len(SPRITE_SCALES)
        self.result_sprites = [None] * len(SPRITE_SCALES)

        def choose_operation():
            if random.random() < 0.5: return None
            return random.choice(list(OPERATIONS))

        shape = hexagonal_loop(Coords(0, 0), 1, lambda x, y: x, True)
        self.configuration = {pos: choose_operation() for pos in shape}

    def setup(self, tiles, center: Coords):
        result_tiles = dict()
        for coords in self.configuration:
            result_tiles[coords] = copy(tiles[center+coords])
            if self.configuration[coords] is None: continue
            self.configuration[coords](result_tiles[coords])
            
        for i, scale in enumerate(SPRITE_SCALES):
            self.sprites[i] = arcade.SpriteList()
            self.result_sprites[i] = arcade.SpriteList()
            for coords in self.configuration:
                self.result_sprites[i].append(result_tiles[coords].sprites[i])
                
                if self.configuration[coords] is None: continue
                tmp = arcade.Sprite(OPERATIONS[self.configuration[coords]], scale)
                tmp.center_x, tmp.center_y = result_tiles[coords].center_pixel(i)
                self.sprites[i].append(tmp)

    def __call__(self, tiles, center: Coords):
            for conf_pos, coords in [(conf, center+conf) for conf in self.configuration]:
                if conf_pos is None: continue
                operation = OPERATIONS[conf_pos]
                if operation is not None: operation(tiles[coords])

    @staticmethod
    def explode(tile: Tile):
        if tile.terrain != TERRAIN_TYPES['rocky']:
            tile.altitude -= 1
        tile.terrain = TERRAIN_TYPES['rough']

    @staticmethod
    def bombard(tile: Tile):
        tile.altitude += 1
        tile.terrain = TERRAIN_TYPES['rough']

    @staticmethod
    def grind_up(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['rough']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['soil']
        
    @staticmethod
    def burn(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['rough']
        elif tile.terrain == TERRAIN_TYPES['soil']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['ice']:
            tile.terrain = TERRAIN_TYPES['soil']
            tile.altitude -= 1

    @staticmethod
    def add_ice(tile: Tile):
        if tile.terrain in [TERRAIN_TYPES['sand'], TERRAIN_TYPES['soil']]:
            tile.terrain = TERRAIN_TYPES['ice']

    def rotate(rotation: int):
        rotation = rotation % 6
        new_config = dict()
        for origin, result in [(dir, (dir+rotation)%6) for dir in range(6)]:
            new_config[result] = self.configuration[origin]
        self.configuration = new_config

    def draw(self, scale):
        self.result_sprites[scale].draw()
        self.sprites[scale].draw()



OPERATIONS = {Terraform.explode: PATH_TO_ASSETS+'terraform_explode.png',
              Terraform.bombard: PATH_TO_ASSETS+'terraform_bombard.png',
              Terraform.grind_up: PATH_TO_ASSETS+'terraform_grindup.png',
              Terraform.burn: PATH_TO_ASSETS+'terraform_burn.png',
              Terraform.add_ice: PATH_TO_ASSETS+'terraform_add_ice.png'}
