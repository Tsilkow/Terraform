from tile import *
from building import *
from interface import *


class Colony(object):
    def __init__(self, interface: Interface, base: Tile,
                 resources: Resources=Resources({'money': 1000, 'concrete': 1000, 'steel': 100})):
        self.interface = interface
        self.base_coords = base.coords
        self.tiles = dict()
        self.buildings = dict()
        self.resources = resources
        self.resource_balance = Resources()
        self.population = 0
        self.workers = 0
        self.housing = 0
        self.add_building(base, BUILDING_TYPES['base'])

    def update(self):
        for res in self.resources.keys():
            self.interface.update_resource(res, self.resources[res], self.resource_balance[res])
        self.interface.update_population(self.population, self.workers, self.housing)

    def _add_tile(self, tile: Tile):
        if tile.coords in self.tiles: return False
        self.tiles[tile.coords] = tile
        return True

    def add_infra(self, tile: Tile, infra_type):
        if (self.resources - INFRA_TYPES[infra_type]['cost']).deficit(): return False
        self._add_tile(tile)
        setattr(tile, infra_type, True)
        self.resources -= INFRA_TYPES[infra_type]['cost']
        self.update()
        
        return True

    def add_building(self, tile: Tile, building_type: BuildingType):
        total_cost = building_type.cost
        infra_needed = []
        for infra in INFRA_TYPES:
            if getattr(building_type, f'{infra}_needed') and not getattr(tile, infra):
                infra_needed.append(infra)
                total_cost += INFRA_TYPES[infra]['cost']
                
        if (self.resources - total_cost).deficit(): return False
        self._add_tile(tile)
        tile.building = Building(building_type, tile, self)
        tile.building.setup()
        self.buildings[tile.coords] = tile.building
        for infra in infra_needed:
            setattr(tile, infra, True)
        self.resources -= total_cost
        self.project_tick()
        
        return True

    def project_tick(self):
        self.workers = self.population
        self.housing = 0
        self.resource_balance = Resources()
        for b in self.buildings.values():
            self.resource_balance, self.workers, self.housing = \
                b.tick(self.resource_balance, self.workers, self.housing)
        self.update()

    def tick(self):
        self.project_tick()
        self.resources -= self.resource_balance
        
