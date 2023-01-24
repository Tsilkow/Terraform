import random

from tile import *


class Terraform(object):
    operations = []
    
    def __init__(self):
        self.configuration = dict()

        def choose_operation():
            if random.random() < 0.5: return None
            return random.choice(self.operations)

        shape = hexagonal_loop(Coords(0, 0), 1, lambda x, y: x, True)
        self.configuration = {pos: choose_operation() for pos in shape}

    def __call__(self, tiles, center: Coords):
        for conf_pos, coords in [(conf, center+conf) for conf in self.configuration]:
            operation = self.operations[conf_pos]
            if operation is not None: operation(tiles[coords])

    @staticmethod
    def explode(tile: Tile):
        if tile.terrain != TERRAIN_TYPES['rocky']:
            tile.altitude -= 1
        tile.terrain = TERRAIN_TYPES['rough']
        tile.building = None

    @staticmethod
    def bombard(tile: Tile):
        tile.altitude += 1
        tile.terrain = TERRAIN_TYPES['rough']
        tile.building = None

    @staticmethod
    def grind_up(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['rough']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['soil']
        
    @staticmethod
    def heat_up(tile: Tile):
        if tile.terrain == TERRAIN_TYPES['sand']: tile.terrain = TERRAIN_TYPES['rough']
        elif tile.terrain == TERRAIN_TYPES['soil']: tile.terrain = TERRAIN_TYPES['sand']
        elif tile.terrain == TERRAIN_TYPES['ice']:
            tile.terrain = TERRAIN_TYPES['soil']
            tile.altitude -= 1

    @staticmethod
    def add_ice(tile: Tile):
        if tile.terrain in [TERRAIN_TYPES['sand'], TERRAIN_TYPES['soil']]:
            tile.terrain = TERRAIN_TYPES['ice']
            
    operations = [explode, bombard, grind_up, heat_up, add_ice]

    def rotate(rotation: int):
        rotation = rotation % 6
        new_config = dict()
        for origin, result in [(dir, (dir+rotation)%6) for dir in range(6)]:
            new_config[result] = self.configuration[origin]
        self.configuration = new_config
