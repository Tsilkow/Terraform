import arcade

from copy import copy
import random

from tile import *


class Terraform(object):
    operations = []
    
    def __init__(self):
        self.configuration = dict()

        def choose_operation():
            if random.random() < 0.5: return None
            return random.choice(list(OPERATIONS))

        shape = hexagonal_loop(Coords(0, 0), 1, lambda x, y: x, True)
        self.configuration = {pos: choose_operation() for pos in shape}

    def setup(self, tiles):
                
        def morph(center):
            morphed_tiles = dict()
            result_sprites = []
            for coords in self.configuration:
                if coords+center in tiles:
                    morphed_tiles[coords+center] = copy(tiles[center+coords])
            self(morphed_tiles, center)

            for coords in self.configuration:
                if self.configuration[coords] is None or coords+center not in tiles: continue
                morphed_tiles[coords+center].setup(tiles)
                icon = []
                for i, scale in enumerate(SPRITE_SCALES):
                    icon.append(arcade.Sprite(OPERATIONS[self.configuration[coords]], scale))
                    center_pixel = morphed_tiles[coords+center].center_pixel(i)
                    icon[i].center_x = center_pixel[0]
                    icon[i].center_y = center_pixel[1]
                        
                result_sprites.append(
                    (coords+center, 'projection', morphed_tiles[coords+center].terrain_sprites))
                result_sprites.append(
                    (coords+center, 'icon', icon))
            return result_sprites

        return morph

    def __call__(self, tiles, center: Coords):
        for conf_pos, coords in [(conf, center+conf) for conf in self.configuration]:
            if conf_pos is None or coords not in tiles: continue
            operation = self.configuration[conf_pos]
            if operation is not None:
                operation(tiles[coords])
                
        for coords in [center+conf for conf in self.configuration]:
            tiles[coords].setup(tiles)

    @staticmethod
    def explode(tile: Tile):
        if tile.terrain != TERRAIN_TYPES['mountain']:
            tile.altitude -= 1
        if tile.terrain in [TERRAIN_TYPES['water'],  TERRAIN_TYPES['ice']]:
            tile.terrain = TERRAIN_TYPES['sand']
        else: tile.terrain = TERRAIN_TYPES['rocky']

    @staticmethod
    def elevate(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['mountain']: return
        tile.altitude += 1
        if tile.terrain != TERRAIN_TYPES['water']: 
            tile.terrain = TERRAIN_TYPES['sand']

    @staticmethod
    def pulverize(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['rocky']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['ground']
        
    @staticmethod
    def melt(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['rocky']
        elif tile.terrain == TERRAIN_TYPES['ground']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['ice']: tile.terrain = TERRAIN_TYPES['water']
        elif tile.terrain == TERRAIN_TYPES['water']:
            tile.terrain = TERRAIN_TYPES['sand']
            tile.altitude -= 1

    @staticmethod
    def comet(tile: Tile):
        if tile.terrain in [TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']]:
            tile.terrain = TERRAIN_TYPES['ice']

    def rotate(self, rotation: int):
        rotation = rotation % 6
        new_config = dict()
        new_config[Coords(0, 0)] = self.configuration[Coords(0, 0)]
        for origin, result in [(dir, (dir+rotation)%6) for dir in range(6)]:
            new_config[direction(result)] = self.configuration[direction(origin)]
        self.configuration = new_config



OPERATIONS = {Terraform.explode: PATH_TO_ASSETS+'terraform_explode.png',
              Terraform.elevate: PATH_TO_ASSETS+'terraform_elevate.png',
              Terraform.pulverize: PATH_TO_ASSETS+'terraform_pulverize.png',
              Terraform.melt: PATH_TO_ASSETS+'terraform_melt.png',
              Terraform.comet: PATH_TO_ASSETS+'terraform_comet.png'}
