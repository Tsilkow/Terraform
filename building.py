import arcade

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

    def __add__(self, other):
        result = Resources()
        for res in self:
            result[res] = self[res]

        for res in other:
            if res not in result: result[res] = 0
            result[res] += other[res]
        return result

    def __sub__(self, other):
        result = Resources()
        for res in self:
            result[res] = self[res]

        for res in other:
            if res not in result: result[res] = 0
            result[res] -= other[res]
        return result

    def deficit(self):
        for res in self:
            if self[res] < 0: return True
        return False


class BuildingType(object):
    def __init__(self, name: str, sprite_filename: str, cost: Resources=None,
                 produces: Resources=None, consumes: Resources=None, housing: int=0,
                 transport_capacity: int=0, terrain_allowed=None, ore_requirement=None):
        self.name = name
        self.sprite_filename = sprite_filename
        if cost is None: self.cost = Resources()
        else: self.cost = cost
        if produces is None: self.produces = Resources()
        else: self.produces = produces
        if consumes is None: self.consumes = Resources()
        else: self.consumes = consumes
        self.housing = housing
        self.transport_capacity = transport_capacity
        self.terrain_allowed = terrain_allowed
        self.ore_requirement = ore_requirement
        
        if self.consumes['energy'] > 0 or self.produces['energy'] > 0 or self.housing > 0:
            self.wires_needed = True
        else: self.wires_needed = False
        if self.consumes['water'] > 0 or self.produces['water'] > 0 or self.housing > 0:
            self.pipes_needed = True
        else: self.pipes_needed = False
        if self.housing > 0: self.tunnels_needed = True
        else:
            self.tunnels_needed = False
            for res in ['food', 'concrete', 'steel', 'electronics', 'spices']:
                if self.consumes[res] > 0 or self.produces[res] > 0:
                    self.tunnels_needed = True
                    break

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
    'shuttle pad': BuildingType(
        'Shuttle Pad', PATH_TO_ASSETS+'building_shuttle_pad.png',
        cost=Resources({'concrete': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']],
        transport_capacity=10),
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
    'water pump': BuildingType(
        'Water Pump', PATH_TO_ASSETS+'building_water_pump.png',
        cost=Resources({'concrete': 10, 'steel': 10}),
        produces=Resources({'water': 40}),
        consumes=Resources({'energy': 10}),
        terrain_allowed=[TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']],
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

INFRA_TYPES = {
    'tunnels': {
        'cost': Resources({'concrete': 5}),
        'terrain_allowed': [TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground']]
    },
    'wires': {
        'cost': Resources({'concrete': 5}),
        'terrain_allowed': [TERRAIN_TYPES['rocky'], TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground'], TERRAIN_TYPES['water'], TERRAIN_TYPES['ice']]
    },
    'pipes': {
        'cost': Resources({'concrete': 1}),
        'terrain_allowed': [TERRAIN_TYPES['rocky'], TERRAIN_TYPES['sand'], TERRAIN_TYPES['ground'], TERRAIN_TYPES['water'], TERRAIN_TYPES['ice']]
    }
}


class Building(object):
    def __init__(self, building_type: BuildingType, tile: Tile, owner: None):
        self.building_type = building_type
        self.tile = tile
        self.owner = owner
        self.active = True
        self.sprites = None

    def setup(self):
        self.sprites = []
        for i, scale in enumerate(SPRITE_SCALES):
            self.sprites.append(arcade.Sprite(self.building_type.sprite_filename, scale))
            self.sprites[i].center_x, self.sprites[i].center_y = self.tile.center_pixel(i)

    def calculate_balance(self):
        if self.active: return self.building_type.produces - self.building_type.consumes
        else: return Resources()

    def tick(self, budget):
        self.active = True
        if self.building_type.tunnels_needed and not self.tile.tunnels: self.active = False
        if self.building_type.pipes_needed and not self.tile.pipes: self.active = False
        if self.building_type.wires_needed and not self.tile.wires: self.active = False
        if self.active:
            balance = calculate_balance()
            if (budget+balance).deficit(): self.active = False
            else: budget += balance
        return budget    

    def __repr__(self):
        return f'{self.building_type.name} at {self.tile.coordinates} | ' \
            f'{self.owner if self.owner is not None else "abandoned"} |'


def project_building(tiles, building_type):

    def build(center):
        if center not in tiles: return None
        valid = True
        if tiles[center].building is not None: valid = False
        if tiles[center].terrain not in building_type.terrain_allowed: valid = False
        sprites = []
        for i, scale in enumerate(SPRITE_SCALES):
            sprites.append(arcade.Sprite(building_type.sprite_filename, scale))
            sprites[i].center_x, sprites[i].center_y = tiles[center].center_pixel(i)
            if not valid: sprites[i].color = [255, 0, 0]
            
        return [(center, 'projection', sprites)], valid

    return build

def project_infra(tiles, infra_type):

    def build(center):
        if center not in tiles: return None
        result = []
        valid = True
        if getattr(tiles[center], infra_type) == True: valid = False
        if tiles[center].terrain not in INFRA_TYPES[infra_type]['terrain_allowed']: valid = False
        if not valid: return result, valid
        
        tmp = tiles[center].get_infra_sprites(tiles, infra_type, True)

        for i, t in enumerate(tmp):
            if t is None: continue
            if i == 0: result.append((center, f'{infra_type}_singular', t))
            else: result.append((center, f'{infra_type}_{i-1}', t))
        
        return result, valid

    return build
