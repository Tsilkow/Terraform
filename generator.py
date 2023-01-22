import numpy as np
from tile import *
import opensimplex


ALTITUDE_DENSITY = 5


class WorldGenerator(object):
    def __init__(self, seed, terrain_types):
        self.seed = seed
        self.terrain_types = terrain_types

    def __call__(self):
        return None


class StandardGenerator(WorldGenerator):
    def __init__(self, seed, terrain_types):
        super().__init__(seed, terrain_types)
        self.radius = 100
        self.altitude_range = (-5, 5)
        self.altitude_noise_amplitude = 3
        self.altitude_density = 10
        self.altitude_max_difference = 3

    def __call__(self):
        result = self.initiate_hexagonal_shape()
        result = self.generate_altitude_from_noise(result)
        result = self.generate_mountain_tops(result)
        
        for tile in result.values():
            tile.setup()

        return result

    # create dictionary of tiles arranged in a shape of a hexagon
    def initiate_hexagonal_shape(self):

        def base_tile_constructor(coords: Coords, loop_coords):
            return Tile(coords, self.terrain_types['sand'])
        
        return tile_list_to_tile_dict(
            hexagonal_loop(Coords(0, 0), self.radius, base_tile_constructor, True))

    # generate altitude from perlin noise and apply it to existing hexagons
    def generate_altitude_from_noise(self, result):
        diameter = 2*self.radius+1
        opensimplex.seed(self.seed)

        for tile in result.values():
            tile.altitude = int(round(
                np.clip(
                    opensimplex.noise2(
                        *self.coords_to_position(
                            tile.coords, self.altitude_density/diameter))
                    , -1, 1)
                * self.altitude_noise_amplitude))

        while(self.find_eccentricites(result, self.altitude_max_difference)): pass
                        
        for tile in result.values():
            for n in [result[coords] for coords in tile.coords.neighbours() if coords in result]:
                diff = tile.altitude - n.altitude
                if abs(diff) > self.altitude_max_difference:
                    print('Altitude over limit!', diff, tile.coords)
        
        return result

    def generate_mountain_tops(self, result):
        for tile in result.values():
            if tile.altitude > 2: tile.terrain = self.terrain_types['rocky']

        return result

    @staticmethod
    def coords_to_position(coords: Coords, scale):
        x = coords.x()*2 * scale 
        y = (coords.z()-coords.y()) * scale
        return x, y
    
    @staticmethod
    def level_eccentricities(a: Tile, b: Tile, max_difference):
        if abs(a.altitude) >= abs(b.altitude):
            eccentricity = a
            other = b
        else:
            eccentricity = b
            other = a

        diff = eccentricity.altitude - other.altitude
        if diff > 0: eccentricity.altitude -= abs(diff) - max_difference
        else: eccentricity.altitude += abs(diff) - max_difference

    @staticmethod
    def find_eccentricites(tiles, max_difference):
        found=False
        for tile in tiles.values():
            for neighbour in [tiles[coords] for coords in tile.coords.neighbours()
                              if coords in tiles]:
                if abs(tile.altitude - neighbour.altitude) > max_difference:
                    found=True
                    StandardGenerator.level_eccentricities(tile, neighbour, max_difference)
        return found
