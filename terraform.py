import arcade

from copy import copy
import random

from tile import *


class Terraform(object):
    operations = []
    
    def __init__(self):
        self.configuration = dict()
        self.icon_sprites = [None] * len(SPRITE_SCALES)

        def choose_operation():
            if random.random() < 0.5: return None
            return random.choice(list(OPERATIONS))

        shape = hexagonal_loop(Coords(0, 0), 1, lambda x, y: x, True)
        self.configuration = {pos: choose_operation() for pos in shape}

    def setup(self, tiles):
                
        def morph(center):
            result_tiles = dict()
            terrain_sprites = dict()
            for coords in self.configuration:
                result_tiles[coords+center] = copy(tiles[center+coords])
            self(result_tiles, center)

            for coords in self.configuration:
                terrain_sprites[coords+center] = result_tiles[coords+center].sprites
            return terrain_sprites

        return morph

    def __call__(self, tiles, center: Coords):
        for conf_pos, coords in [(conf, center+conf) for conf in self.configuration]:
            #print(f'{center}: {conf_pos}, {coords}')
            if conf_pos is None: continue
            operation = self.configuration[conf_pos]
            if operation is not None: operation(tiles[coords])
            tiles[coords].setup()

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
        self.icon_sprites[scale].draw()



OPERATIONS = {Terraform.explode: PATH_TO_ASSETS+'terraform_explode.png',
              Terraform.bombard: PATH_TO_ASSETS+'terraform_bombard.png',
              Terraform.grind_up: PATH_TO_ASSETS+'terraform_grindup.png',
              Terraform.burn: PATH_TO_ASSETS+'terraform_burn.png',
              Terraform.add_ice: PATH_TO_ASSETS+'terraform_add_ice.png'}
