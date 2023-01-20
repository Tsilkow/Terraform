from enum import Enum


# Enumeration of possible terrain types of a tile
class TerrainType(Enum):
    Mountain = 1
    Rough = 2
    Sand = 3
    Soil = 4
    Water = 5
    Ice = 6


# Class for holding coordinates, in particular axial hexagonal coorindates with conversion to cube coordinates
class Coords(object):
    def __init__(self, r: int, q: int):
        self.r = r
        self.q = q

    def __repr__(self):
        return f'({self.r} {self.q} {self.z()})'

    # Axial cooridnates
    def rq(self): return (self.r, self.q)
    # Cube coordinates
    def xyz(self): return (self.r, self.q, self.z())
    def x(self): return self.r
    def y(self): return self.q
    def z(self): return -self.r -self.q
    # Value representing what's closer to the screen
    def priority(self): return 2*self.q + self.r
    

class Tile(object):
    def __init__(self, coordinates: Coords, terrain: TerrainType, altitude):
        self.coordinates = coordinates
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

    def __str__(self):
        return f'{self.terrain} at {self.coorindates}'

    def __repr__(self):
        return f'{self.coordinates}: {self.terrain} | '\
        f'{self.owner.name if self.owner is not None else "abandoned"} | '\
        f'{self.building if self.building is not None else ""}'\
        f'{"tunneled " if self.tunnels else ""}'\
        f'{"wired " if self.wires else ""}'\
        f'{"with plumbing " if self.pipes else ""}'\
        f'{"Ore deposits " if self.ore else ""}'\
        f'{"Silica deposits " if self.silica else ""}'\
        f'{"Gold deposists " if self.gold else ""}'
