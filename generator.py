import numpy as np
from tile import *
from terraform import *
import opensimplex
import random


ALTITUDE_DENSITY = 5


class WorldGenerator(object):
    def __init__(self, seed):
        self.seed = seed

    def __call__(self):
        return None


class StandardGenerator(WorldGenerator):
    """Standard world generator: hexagonal shape, mountain ridges"""
    def __init__(self, seed):
        super().__init__(seed)
        self.radius = 10
        self.altitude_noise_amplitude = 2
        self.altitude_density = 0.1
        self.altitude_max_difference = 3
        self.mountain_ridge_density = 0.005
        self.mountain_ridge_length_range = (10, 15)
        self.mountain_ridge_deviation = 0.5
        self.mountain_rocky_radiation_probability = [0.01, 0.5, 0.75, 0.875, 0.875, 0.875, 0.5]
        self.rocky_rocky_radiation_probability = [0, 0.5, 0.75, 0.875, 0.875, 0.875, 0.5]
        self.rocky_rocky_radiation_repeats = 3

    def __call__(self):
        print('Generating world map:')

        terraform = Terraform()
        print(terraform.configuration)
        
        result = self.initiate_hexagonal_shape()
        result = self.generate_altitude_from_noise(result)
        result = self.generate_mountains(result)
        result = self.generate_rocky_terrain(result)
        result = self.finalize_tiles(result)

        print('Generation complete!')
        return result

    def finalize_tiles(self, tiles):
        print('Finalizing tiles ...', end='\r')
        
        for tile in tiles.values():
            tile.setup()

        print('Finalizing tiles [DONE]')
        return tiles

    def initiate_hexagonal_shape(self):
        """
        Creates sand tiles put together in a hexagonal shape
        """
        print('Initiating map ...', end='\r')
        
        def base_tile_constructor(coords: Coords, loop_coords):
            return Tile(coords, TERRAIN_TYPES['sand'])
        
        tiles = tile_list_to_tile_dict(
            hexagonal_loop(Coords(0, 0), self.radius,base_tile_constructor, True))
        
        print('Initiating map [DONE]')
        return tiles

    def generate_altitude_from_noise(self, tiles):
        """
        Modifies existing tiles to have altitudes set according to 
        simplex noise
        """
        print('Generating heightmap ...', end='\r')
        opensimplex.seed(self.seed)

        for tile in tiles.values():
            samples = [c*self.altitude_density for c in tile.coords.center()]
            noise = np.clip(opensimplex.noise2(*samples), -1, 1)
            tile.altitude = int(round(noise * self.altitude_noise_amplitude))

        while(self.find_eccentricites(tiles, self.altitude_max_difference)): pass
                        
        for tile in tiles.values():
            for n in [tiles[coords]
                      for coords in tile.coords.neighbours()
                      if coords in tiles]:
                diff = tile.altitude - n.altitude
                if abs(diff) > self.altitude_max_difference:
                    print('Altitude over limit!', diff, tile.coords)
        
        print('Generating heightmap [DONE]')
        return tiles

    def find_feasable_ridge_ends(self, tiles, mountain_occupied):

        def mark_candidate(coords, loop_indices):
            if loop_indices[0] in range(
                    *self.mountain_ridge_length_range):
                return coords
            return None
        
        start, end = None, None
        while start is None or end is None:
            start = random.choice(list(tiles))
            if (start in mountain_occupied): continue
            
            candidates = hexagonal_loop(
                start, self.mountain_ridge_length_range[1],
                mark_candidate, True)
            candidates = [c for c in candidates
                          if c is not None
                          and c in tiles
                          and c not in mountain_occupied]

            if len(candidates) == 0: continue
            end = random.choice(candidates)
            for c in coords_in_between(start, end):
                if c not in tiles or c in mountain_occupied:
                    end = None

        return start, end

    
    def find_feasable_ridge_chain(self, tiles, start, end):
        dist = distance(start, end)
        if dist == 1: return []
        middle = None
        while (middle is None
               or middle not in tiles
               or middle == start
               or middle == end):
            if dist == 2:
                middle = random.choice(
                    list(set(start.neighbours())
                         & set(end.neighbours())))
            elif dist > 2:
                amplitude = max(1, int(round(
                    dist * self.mountain_ridge_deviation)))
                mid_x = ((start.center()[0] + end.center()[0])//2 + 
                         random.randrange(-amplitude+1, amplitude))
                mid_y = ((start.center()[1] + end.center()[1])//2 + 
                         random.randrange(-amplitude+1, amplitude))
                middle = center_to_coords(mid_x, mid_y)
                #print(mid_x, mid_y)
                #print(start.center(), middle.center(), end.center())

        ridge1 = self.find_feasable_ridge_chain(tiles, start, middle)
        ridge2 = self.find_feasable_ridge_chain(tiles, middle, end)
        return ridge1 + [middle] + ridge2

    def generate_mountains(self, tiles):
        tiles, mountain_occupied = self.generate_mountain_ridges(tiles)
        tiles = self.generate_mountain_bases(tiles, mountain_occupied)
        
        return tiles
                
    def generate_mountain_ridges(self, tiles):
        """
        Randomly creates non-overlaping mountain ridges of 
        a length within a preset range and changes tiles in 
        the way of the mountain ridge to be mountain and be higher
        """
        print('Generating mountain ridges ...', end='\r')
        mountain_ridge_total = int(round(self.mountain_ridge_density * len(tiles)))
        mountain_occupied = set()
        for i in range(mountain_ridge_total):
            start, end = self.find_feasable_ridge_ends(tiles, mountain_occupied)
            chain = ([start]
                     + self.find_feasable_ridge_chain(tiles, start, end)
                     + [end])
            for coords in chain:
                if coords in mountain_occupied: continue
                tiles[coords].terrain = TERRAIN_TYPES['mountain']
                tiles[coords].altitude += 3
                mountain_occupied.add(coords)
        
        print('Generating mountain ridges [DONE]')
        return tiles, mountain_occupied
    
    def generate_mountain_bases(self, tiles, mountain_occupied):
        print('Generating mountain bases ...', end='\r')

        def get_lower_adjacent(origins):
            result = dict()
            for position in origins:
                radiated_altitude = tiles[position].altitude-2
                for n in position.neighbours():
                    if n not in tiles: continue
                    if radiated_altitude <= tiles[n].altitude: continue
                    if n in result and result[n] >= radiated_altitude: continue
                    result[n] = radiated_altitude
            return result
        
        current = get_lower_adjacent(mountain_occupied)
        while len(current) > 0:
            for position in current:
                tiles[position].terrain = TERRAIN_TYPES['mountain']
                tiles[position].altitude = current[position]
            current = get_lower_adjacent(list(current))
        
        print('Generating mountain bases [DONE]')
        return tiles

    def generate_rocky_terrain(self, tiles):
        print('Generating rocky terrain ...', end='\r')
        
        tiles = self.radiate_terrain(
            tiles, TERRAIN_TYPES['sand'], TERRAIN_TYPES['rocky'],
            TERRAIN_TYPES['mountain'], self.mountain_rocky_radiation_probability)
        for _ in range(self.rocky_rocky_radiation_repeats):
            tiles = self.radiate_terrain(
                tiles, TERRAIN_TYPES['sand'], TERRAIN_TYPES['rocky'],
                TERRAIN_TYPES['rocky'], self.rocky_rocky_radiation_probability)

        print('Generating rocky terrain [DONE]')
        return tiles

    def radiate_terrain(self, tiles, substract: TerrainType, product: TerrainType,
                        catalizer: TerrainType, probabilities):

        if catalizer == None: origins = list(tiles)
        else: origins = [tile.coords for tile in tiles.values() if tile.terrain == catalizer]
        candidates = StandardGenerator.get_adjacent(tiles, origins)
        candidates = [c for c in candidates if tiles[c].terrain == substract]
        candidates = {c: len(c.neighbours()) for c in candidates}
        for coords in list(tiles):
            if coords not in candidates: candidates[coords] = 0
        chosen = [c for c in candidates if random.random() < probabilities[candidates[c]]]
        for c in chosen: tiles[c].terrain = product

        return tiles

    @staticmethod
    def get_adjacent(tiles, origins):
        result = set()
        for position in origins:
            real_neighbours = [n for n in position.neighbours() if n in tiles]
            result.update(real_neighbours)

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
        to_norm = 2*(diff>0)-1
        eccentricity.altitude += (to_norm
                                  * (abs(diff) - max_difference))

    @staticmethod
    def find_eccentricites(tiles, max_difference):
        found=False
        for tile in tiles.values():
            neighbours = [tiles[coords]
                          for coords in tile.coords.neighbours()
                          if coords in tiles]
            for neighbour in neighbours:
                if (abs(tile.altitude - neighbour.altitude)
                    > max_difference):
                    found=True
                    StandardGenerator.level_eccentricities(
                        tile, neighbour, max_difference)
        return found
