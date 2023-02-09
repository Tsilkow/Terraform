from typing import Callable
from itertools import product


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


def coords_in_between(a: Coords, b: Coords):

    def linear_interpolation(start: int, end: int, t: float):
        assert t >= 0, t <= 1
        return int(round(start*(1-t) + end*t))

    def coords_interpolation(start: Coords, end: Coords, t: float):
        return Coords(linear_interpolation(start.r, end.r, t),
                      linear_interpolation(start.q, end.q, t))
    
    result = []
    dist = distance(a, b)
    for d in range(dist+1):
        result.append(coords_interpolation(a, b, d/dist))

    return result
