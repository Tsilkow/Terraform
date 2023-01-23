import numpy as np
from tile import *
import opensimplex
import random


ALTITUDE_DENSITY = 5


class WorldGenerator(object):
    def __init__(self, seed, terrain_types):
        self.seed = seed
        self.terrain_types = terrain_types

    def __call__(self):
        return None


class StandardGenerator(WorldGenerator):
    '''
    Standard world generator: hexagonal shape, mountain ridges
    '''
    def __init__(self, seed, terrain_types):
        super().__init__(seed, terrain_types)
        self.radius = 100
        self.altitude_range = (-5, 5)
        self.altitude_noise_amplitude = 3
        self.altitude_density = 10
        self.altitude_max_difference = 3
        self.mountain_ridge_density = 0.002
        self.mountain_ridge_length_range = (20, 30)
        self.mountain_ridge_deviation = 0

    def __call__(self):
        result = self.initiate_hexagonal_shape()
        result = self.generate_altitude_from_noise(result)
        #result = self.generate_mountain_tops(result)
        result = self.generate_mountain_ridges(result)
        
        for tile in result.values():
            tile.setup()

        return result

    def initiate_hexagonal_shape(self):
        '''
        Creates sand tiles put together in a hexagonal shape
        '''
        def base_tile_constructor(coords: Coords, loop_coords):
            return Tile(coords, self.terrain_types['sand'])
        
        return tile_list_to_tile_dict(
            hexagonal_loop(Coords(0, 0), self.radius, base_tile_constructor, True))

    # generate altitude from perlin noise and apply it to existing hexagons
    def generate_altitude_from_noise(self, result):
        '''
        Modifies existing tiles to have altitudes set according to simplex noise
        '''
        diameter = 2*self.radius+1
        opensimplex.seed(self.seed)

        for tile in result.values():
            tile.altitude = int(round(
                np.clip(
                    opensimplex.noise2(
                        *[c*self.altitude_density/diameter for c in tile.coords.center()])
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

    def find_feasable_ridge_ends(self, result, mountain_occupied):
        start, end = None, None
        while start is None or end is None:
            start = random.choice(list(result))
            if result[start].terrain != 'rocky' and start not in mountain_occupied:
                
                def mark_candidate(coords, loop_indices):
                    if loop_indices[0] in range(*self.mountain_ridge_length_range):
                        return coords
                    return None

                candidates = hexagonal_loop(start, self.mountain_ridge_length_range[1], mark_candidate, True)
                candidates = [c for c in candidates
                              if c is not None and
                              c in result and
                              result[c].terrain != 'rocky' and
                              c not in mountain_occupied]

                if len(candidates) == 0: continue
                end = random.choice(candidates)

        return start, end

    
    def find_feasable_ridge_chain(self, result, mountain_occupied, start, end):
        dist = distance(start, end)
        if dist == 1: return []
        middle = None
        while middle is None or middle not in result or middle == start or middle == end:# or middle in mountain_occupied:
            if dist == 2:
                middle = random.choice(list(set(start.neighbours()) & set(end.neighbours())))
            elif dist > 2:
                amplitude = max(1, int(round(dist * self.mountain_ridge_deviation)))
                mid_x = (start.center()[0] + end.center()[0])//2 + \
                    random.randrange(-amplitude+1, amplitude)
                mid_y = (start.center()[1] + end.center()[1])//2 + \
                    random.randrange(-amplitude+1, amplitude)
                middle = center_to_coords(mid_x, mid_y)
                #print(mid_x, mid_y)
                #print(start.center(), middle.center(), end.center())

        #print(start, middle, end)
        return self.find_feasable_ridge_chain(result, mountain_occupied, start, middle) + \
            [middle] + self.find_feasable_ridge_chain(result, mountain_occupied, middle, end)
                

    def generate_mountain_ridges(self, result):
        '''
        Randomly creates non-overlaping mountain ridges of a length within a preset range and changes tiles in the way of the mountain ridge to be rocky and be higher
        '''
        mountain_ridge_total = int(round(self.mountain_ridge_density * len(result)))
        print(mountain_ridge_total)
        mountain_occupied = set()
        for i in range(mountain_ridge_total):
            start, end = self.find_feasable_ridge_ends(result, mountain_occupied)
            chain = [start] + self.find_feasable_ridge_chain(result, mountain_occupied, start, end) + [end]
            for coords in chain:
                result[coords].terrain = self.terrain_types['rocky']
                mountain_occupied.add(coords)
        
        return result
    
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
