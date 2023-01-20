from collections import namedtuple

from tile import *


Resources = namedtuple('Resources', ['money', 'workers', 'housing', 'energy',
                                     'water', 'food', 'minerals', 'glass',
                                     'spices', 'electronics'])


class BuildingType(object):
    def __init__(self, name: str, cost: Resources, produces: Resources, ingredient_use: Resources):
        self.name = name
        self.cost = cost
        self.produces = produces
        self.ingredient_use = ingredient_use

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name}: \n' \
            f'costs {self.cost} \n' \
            f'produces {self.produces} \n' \
            f'ingredient use {self.ingredient_use} \n'


class Building(object):
    def __init__(self, building_type: BuildingType, tile: Tile, owner: None):
        self.building_type = building_type
        self.tile = tile
        self.owner = owner

    def __repr__(self):
        return f'{self.building_type.name} at {self.tile.coordinates} | ' \
            f'{self.owner if self.owner is not None else "abandoned"} |'
