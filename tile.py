import arcade

from coords import *


HEX_WIDTH = 120
HEX_HEIGHT = 104
HEX_QUARTER = 30
HEX_OFFSET = 30
ALTITUDE_TO_Y = 10
ALTITUDE_SHADING = 10
SPRITE_SCALES = [0.25, 0.5, 1.0]

PATH_TO_ASSETS = 'assets/'


# Enumeration of possible terrain types of a tile
class TerrainType(object):
    def __init__(self, name, sprite_filename):
        self.name = name
        self.sprite_filename = sprite_filename

    def __str__(self):
        return self.name

    
TERRAIN_TYPES = {
    'mountain': TerrainType('Mountain', PATH_TO_ASSETS+'terrain_mountain.png'),
    'rocky': TerrainType('Rocky', PATH_TO_ASSETS+'terrain_rocky.png'),
    'sand' : TerrainType('Sand' , PATH_TO_ASSETS+'terrain_sand.png' ),
    'ground' : TerrainType('Ground' , PATH_TO_ASSETS+'terrain_ground.png' ),
    'water': TerrainType('Water', PATH_TO_ASSETS+'terrain_water.png'),
    'ice'  : TerrainType('Ice'  , PATH_TO_ASSETS+'terrain_ice.png'  )
}


TUNNEL_SPRITES = [
    PATH_TO_ASSETS+'tunnels.png', 
    PATH_TO_ASSETS+'tunnels_0.png', 
    PATH_TO_ASSETS+'tunnels_1.png', 
    PATH_TO_ASSETS+'tunnels_2.png', 
    PATH_TO_ASSETS+'tunnels_3.png', 
    PATH_TO_ASSETS+'tunnels_4.png', 
    PATH_TO_ASSETS+'tunnels_5.png']
    

class Tile(object):
    def __init__(self, coords: Coords, terrain: TerrainType,
                 altitude=0):
        self.coords = coords
        self.terrain = terrain
        self.altitude = altitude
        self.building = None
        self.owner = None
        self.tunnels = False
        self.wires = False
        self.pipes = False
        self.ore = False
        self.silica = False
        self.gold = False

        self.terrain_sprites = [None]*len(SPRITE_SCALES)
        self.tunnel_sprites = [None]*7

    def setup(self, tiles):
        tunnel_connections = []
        if self.tunnels:
            for i, n in enumerate(self.coords.neighbours()):
                if n not in tiles: continue
                if abs(self.altitude - tiles[n].altitude) > 1: continue
                if tiles[n].tunnels: tunnel_connections.append(i)
            
        for i, scale in enumerate(SPRITE_SCALES):
            self.terrain_sprites[i] = arcade.Sprite(self.terrain.sprite_filename, scale)
            self.terrain_sprites[i].color = [
                int(round(255 + (self.altitude-5)*(ALTITUDE_SHADING))) for _ in range(3)]
            self.terrain_sprites[i].center_x, self.terrain_sprites[i].center_y = \
                self.center_pixel(i)
            for j in tunnel_connections:
                if i == 0: self.tunnel_sprites[j+1] = []
                self.tunnel_sprites[j+1].append(arcade.Sprite(TUNNEL_SPRITES[j+1], scale))
                self.tunnel_sprites[j+1][i].color = [
                    int(round(255 + (self.altitude-5)*(ALTITUDE_SHADING))) for _ in range(3)]
                self.tunnel_sprites[j+1][i].center_x, self.tunnel_sprites[j+1][i].center_y = \
                    self.center_pixel(i)

    def __copy__(self):
        tmp = Tile(self.coords, self.terrain, self.altitude)
        tmp.ore = self.ore
        tmp.silica = self.silica
        tmp.gold = self.gold
        
        return tmp

    def __str__(self):
        return f'{self.terrain} at {self.coords}'

    def __repr__(self):
        return f'{self.coords}: {self.terrain} | '\
        f'{self.owner.name if self.owner is not None else "abandoned"} | '\
        f'{self.building if self.building is not None else ""}'\
        f'{"tunneled " if self.tunnels else ""}'\
        f'{"wired " if self.wires else ""}'\
        f'{"with plumbing " if self.pipes else ""}'\
        f'{"Ore deposits " if self.ore else ""}'\
        f'{"Silica deposits " if self.silica else ""}'\
        f'{"Gold deposists " if self.gold else ""}'
    
    def center_pixel(self, scale_index):
        center = self.coords.center()
        x = int(round((HEX_WIDTH - HEX_QUARTER) * center[0]/2 * SPRITE_SCALES[scale_index]))
        y = int(round((HEX_HEIGHT * center[1]/2 + self.altitude*ALTITUDE_TO_Y - HEX_OFFSET//2)
                      * SPRITE_SCALES[scale_index]))
        return x, y


def pixel_to_coords(pixel, scale):
    center_x = int(round(pixel[0] / SPRITE_SCALES[scale] / (HEX_WIDTH - HEX_QUARTER) * 2))
    center_y = int(round(
        (pixel[1] + HEX_OFFSET//2)*2 / HEX_HEIGHT / SPRITE_SCALES[scale]))
    return center_to_coords(center_x, center_y)
    

def tile_list_to_tile_dict(tile_list: list):
    tile_dict = dict()
    for tile in tile_list:
        tile_dict[tile.coords] = tile

    return tile_dict
