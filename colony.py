from tile import *
from building import *
from interface import *


class Colony(object):
    def __init__(self, interface: Interface, base: Tile,
                 resources: Resources=Resources({'money': 1000})):
        self.interface = interface
        self.base_coords = base.coords
        self.tiles = dict()
        self.buildings = dict()
        self.resources = resources
        self.resource_balance = Resources()
        self.add_building(base, BUILDING_TYPES['base'])

    def update(self):
        for (res, val) in self.resources.items():
            self.interface.update_resource(res, val)

    def add_tile(self, tile: Tile):
        if tile.coords in self.tiles: return False
        self.tiles[tile.coords] = tile
        return True

    def add_building(self, tile: Tile, building_type: BuildingType):
        if (self.resources - building_type.cost).deficit(): return False
        self.add_tile(tile)
        tile.building = Building(building_type, tile, self)
        tile.building.setup()
        self.buildings[tile.coords] = tile.building
        self.resources -= building_type.cost
        self.update()
        
        return True

    def calculate_balance(self):
        for b in self.buildings:
            self.resource_balance += b.calculate_balance()
        self.update()

    def tick(self):
        for b in self.buildings:
            self.resources = b.tick(self.resources)
        self.update()
        
