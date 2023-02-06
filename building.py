import arcade

from collections import namedtuple

from tile import *


#Resources = namedtuple('Resources', ['money', 'workers', 'housing', 'energy',
#                                     'water', 'food', 'concrete', 'steel',
#                                     'spices', 'electronics'])
class Resources(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        if 'money' not in self: self['money'] = 0
        if 'energy' not in self: self['energy'] = 0
        if 'water' not in self: self['water'] = 0
        if 'food' not in self: self['food'] = 0
        if 'concrete' not in self: self['concrete'] = 0
        if 'steel' not in self: self['steel'] = 0
        if 'electronics' not in self: self['electronics'] = 0
        if 'spices' not in self: self['spices'] = 0


class BuildingType(object):
    def __init__(self, name: str, sprite_filename: str, cost: Resources=None,
                 produces: Resources=None, consumes: Resources=None, housing: int=0,
                 terrain_allowed=None, ore_requirement=None):
        self.name = name
        self.sprite_filename = sprite_filename
        if cost is None: self.cost = Resources()
        else: self.cost = cost
        if produces is None: self.produces = Resources()
        else: self.produces = produces
        if consumes is None: self.consumes = Resources()
        else: self.consumes = consumes
        self.housing = housing
        self.terrain_allowed = terrain_allowed
        self.ore_requirement = ore_requirement

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name}: \n' \
            f'costs {self.cost} \n' \
            f'produces {self.produces} \n' \
            f'ingredient use {self.consumes} \n'


BUILDING_TYPES = {
    'base': BuildingType(
        'Base', PATH_TO_ASSETS+'building_base.png',
        produces=Resources({'energy': 100, 'water': 10, 'food': 10, 'concrete': 10, 'steel': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']]),
    'shelter': BuildingType(
        'Shelter', PATH_TO_ASSETS+'building_shelter.png',
        cost=Resources({'concrete': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']],
        housing=10),
    'solar panes': BuildingType(
        'Solar Panes', PATH_TO_ASSETS+'building_solar_panes.png',
        cost=Resources({'steel': 10}),
        produces=Resources({'energy': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']]),
    'well': BuildingType(
        'Well', PATH_TO_ASSETS+'building_well.png',
        cost=Resources({'concrete': 10, 'steel': 10}),
        produces=Resources({'water': 40}),
        consumes=Resources({'energy': 10}),
        ore_requirement='water'),
    'greenhouse': BuildingType(
        'Greenhouse', PATH_TO_ASSETS+'building_greenhouse.png',
        cost=Resources({'concrete': 20, 'steel': 5}),
        produces=Resources({'food': 10}),
        consumes=Resources({'energy': 5, 'water': 15}),
        terrain_allowed=[TERRAIN_TYPES['ground']]),
    'concrete plant': BuildingType(
        'Concrete Plant', PATH_TO_ASSETS+'building_concrete_plant.png',
        cost=Resources({'concrete': 20, 'steel': 5}),
        produces=Resources({'concrete': 30}),
        consumes=Resources({'energy': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand']]),
    'steel foundry': BuildingType(
        'Steel Foundry', PATH_TO_ASSETS+'building_steel_foundry.png',
        cost=Resources({'concrete': 30, 'steel': 20}),
        produces=Resources({'concrete': 20}),
        consumes=Resources({'energy': 20}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']],
        ore_requirement='iron')
}


class Building(object):
    def __init__(self, type: BuildingType, tile: Tile, owner: None):
        self.building_type = building_type
        self.tile = tile
        self.owner = owner
        self.sprite = None

    def setup(self):
        for i, scale in enumerate(SPRITE_SCALES):
            self.sprites[i] = arcade.Sprite(self.building_type.sprite_filename, scale)
            self.sprites[i].center_x, self.sprites[i].center_y = self.tile.center_pixel(i)

    def __repr__(self):
        return f'{self.building_type.name} at {self.tile.coordinates} | ' \
            f'{self.owner if self.owner is not None else "abandoned"} |'
