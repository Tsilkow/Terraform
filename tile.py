import arcade
from enum import Enum
from typing import Callable
from itertools import product


HEX_WIDTH =        120 //2
HEX_HEIGHT =       104 //2
HEX_QUARTER =       30 //2
HEX_OFFSET =        30 //2
ALTITUDE_TO_Y =     10 //2
ALTITUDE_SHADING =  10
SPRITE_SCALE  =     0.5


# Enumeration of possible terrain types of a tile
class TerrainType(object):
    def __init__(self, name, sprite_filenames):
        self.name = name
        self.sprite_filenames = sprite_filenames

    def __str__(self):
        return self.name


# 
class Coords(object):
    '''
    Class for holding coordinates, in particular axial hexagonal 
    coorindates with conversion to cube coordinates
    '''
    def __init__(self, r: int, q: int):
        self.r = r
        self.q = q

    def __repr__(self):
        return f'({self.r} {self.q} {self.z()})'

    def __eq__(self, other):
        return self.r == other.r and self.q == other.q

    def __hash__(self):
        return hash((self.r, self.q))

    def __add__(self, other):
        return Coords(self.r + other.r, self.q + other.q)
    
    def __mul__(self, other: int):
        return Coords(self.r * other, self.r * other)

    # Axial cooridnates
    def rq(self): return (self.r, self.q)
    # Cube coords
    def xyz(self): return (self.r, self.q, self.z())
    def x(self): return self.r
    def y(self): return self.q
    def z(self): return -self.r -self.q
    # Value representing what's closer to the screen
    def priority(self): return 2*self.q +self.r
    
    # Position of center of hex using carthesian axis;
    # center of the hex if it was a 2x2 square
    def center(self):
        x = self.x()*2
        y = self.z()-self.y()
        return x, y
    
    def neighbour(self, dir):
        return self + direction(dir)
        
    def neighbours(self):
        return [self + direction(i) for i in range(6)]
        

def direction(dir: int):
    if   dir == 0: return Coords( 0, -1)
    elif dir == 1: return Coords(+1, -1)
    elif dir == 2: return Coords(+1,  0)
    elif dir == 3: return Coords( 0, +1)
    elif dir == 4: return Coords(-1, +1)
    elif dir == 5: return Coords(-1,  0)
    else:          return Coords( 0,  0)


def center_to_coords(x: int, y: int):
    return Coords(x//2, -y//2 - x//4)
    
    
def distance(a: Coords, b: Coords):
    return max(abs(a.x()-b.x()), abs(a.y()-b.y()), abs(a.z()-b.z()))
        

def hexagonal_loop(start: Coords, radius: int, function: Callable,
                   use_memory: bool=False, pass_memory: bool=False):
    assert radius >= 0
    memory = []

    def action(curr, memory, loop_coords):
        if not use_memory:
            function(curr, loop_coords)
            return
        
        if pass_memory:
            memory.append(function(curr, loop_coords, memory))
        else: memory.append(function(curr, loop_coords))
        return memory
    
    curr = start
    memory = action(curr, memory, (0, 0, 0))
    for r in range(1, radius+1):
        curr = curr.neighbour(4)
        for side, step in product(range(6), range(r)):
            memory = action(curr, memory, (r, side, step))
            curr = curr.neighbour(side)

    if use_memory: return memory

def tile_list_to_tile_dict(tile_list: list):
    tile_dict = dict()
    for tile in tile_list:
        tile_dict[tile.coords] = tile

    return tile_dict

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

    def setup(self):
        self.sprite = \
            arcade.Sprite(self.terrain.sprite_filenames, SPRITE_SCALE)
        self.sprite.color = \
            [int(round(255 + (self.altitude-5)*ALTITUDE_SHADING))
             for _ in range(3)]
        self.sprite.center_x, self.sprite.center_y = \
            self.center_pixel()
        self.sprite.center_y -= HEX_OFFSET//2

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
    
    def center_pixel(self):
        center = self.coords.center()
        x = int(round((HEX_WIDTH - HEX_QUARTER) * center[0]/2))
        y = int(round(HEX_HEIGHT * center[1]/2)
                + self.altitude*ALTITUDE_TO_Y)
        return x, y
