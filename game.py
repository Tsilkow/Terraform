import arcade
from pyglet.math import Vec2

import random
from sys import getsizeof

from coords import *
from tile import *
from tilemap import *
from building import *
from colony import *
from terraform import *
from generator import *
from interface import *


RESOLUTION = (1200, 800)
SCREEN_TITLE = 'Terraform'


class Game(arcade.Window):
    def __init__(self, resolution, title):
        super().__init__(resolution[0], resolution[1], title)
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.num_add_pressed = False
        self.num_subtract_pressed = False
        self.q_pressed = False
        self.w_pressed = False
        self.e_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False

        self.cursor_can_move = True
        self.cursor_timer = 0

        self.interface = None
        self.generator = None
        self.colony = None
        self.tilemap = None
        self.cast_terraform = None
        self.cast_building_type = None
        self.cast_infra_type = None
        
    def setup(self):
        self.world_generator = StandardGenerator(2137)
        self.tiles = self.world_generator()
        self.tilemap = Tilemap(RESOLUTION)
        self.tilemap.setup(self.tiles)
        self.interface = Interface(RESOLUTION, Resources().keys())

    def on_draw(self):
        self.clear()

        self.tilemap.draw()

        self.interface.draw()
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.Q:
            self.q_pressed = True
        elif key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.E:
            self.e_pressed = True
        elif key == arcade.key.A:
            self.a_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True
        elif key == arcade.key.D:
            self.d_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.NUM_ADD:
            self.tilemap.zoom(True)
        elif key == arcade.key.NUM_SUBTRACT:
            self.tilemap.zoom(False)
        elif key == arcade.key.Q:
            self.q_pressed = False
        elif key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.E:
            self.e_pressed = False
        elif key == arcade.key.A:
            self.a_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False
        elif key == arcade.key.D:
            self.d_pressed = False
        elif key == arcade.key.R:
            self._rotate_terraform()
        elif key == arcade.key.T:
            self._enter_terraform_mode(Terraform())
        elif key == arcade.key.Y:
            if self._execute_build(): pass
            elif self._execute_terraform(): pass
            elif self._execute_infra_build(): pass
        elif key == arcade.key.B:
            self._iterate_over_buildings()
        elif key == arcade.key.F:
            self._enter_infra_building_mode('tunnels')
        elif key == arcade.key.G:
            self._enter_infra_building_mode('wires')
        elif key == arcade.key.H:
            self._enter_infra_building_mode('pipes')

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        self.tilemap.move_cursor_to_pixel(Vec2(x, y))

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

    def _enter_building_mode(self, building_type: BuildingType):
        self.cast_building_type = building_type
        self.cast_terraform = None
        self.cast_infra_type = None
        self.tilemap.untie_from_cursor()
        self.tilemap.tie_to_cursor(project_building(self.tiles, building_type))

    def _enter_infra_building_mode(self, infra_type: str):
        self.cast_infra_type = infra_type
        self.cast_building_type = None
        self.cast_terraform = None
        self.tilemap.untie_from_cursor()
        self.tilemap.tie_to_cursor(project_infra(self.tiles, infra_type))

    def _enter_terraform_mode(self, terraform=None):
        self.cast_terraform = terraform
        self.cast_building_type = None
        self.cast_infra_type = None
        self.tilemap.untie_from_cursor()
        self.tilemap.tie_to_cursor(self.cast_terraform.setup(self.tiles))

    def _execute_build(self):
        if self.cast_building_type is None: return False
        if not self.tilemap.tied_to_cursor_is_valid: return False
        
        if self.colony is None:
            if self.cast_building_type != BUILDING_TYPES['base']: return False
            self.colony = Colony(self.interface, self.tiles[self.tilemap.cursor_coords])
            self.tilemap.setup(self.tiles)
        else:
            if self.cast_building_type == BUILDING_TYPES['base']: return False
            if self.colony.add_building(self.tiles[self.tilemap.cursor_coords],
                                        self.cast_building_type):
                self.tilemap.setup(self.tiles)
            else: return False
            
        self.tilemap.untie_from_cursor()
        self.cast_building_type = None
        return True
    
    def _execute_infra_build(self):
        if self.cast_infra_type is None: return False
        if not self.tilemap.tied_to_cursor_is_valid: return False
        if self.colony is None: return False

        if self.colony.add_infra(self.tiles[self.tilemap.cursor_coords], self.cast_infra_type):
            self.tilemap.setup(self.tiles)
        else: return False
            
        self.tilemap.untie_from_cursor()
        self.tilemap.setup(self.tiles)
        self.cast_infra_type = None
        return True

    def _execute_terraform(self):
        if self.cast_terraform is None: return False
        if not self.tilemap.tied_to_cursor_is_valid: return False
        self.tilemap.untie_from_cursor()
        self.cast_terraform(self.tiles, self.tilemap.cursor_coords)
        self.tilemap.setup(self.tiles)
        self.cast_terraform = None
        return True

    def _iterate_over_buildings(self, forward: bool=True):
        if self.cast_building_type is None: self._enter_building_mode(BUILDING_TYPES['base'])
        elif self.cast_building_type not in BUILDING_TYPES.values(): pass
        else:
            keys = list(BUILDING_TYPES.keys())
            curr_key = list(BUILDING_TYPES.values()).index(self.cast_building_type)
            if forward: next_key = keys[curr_key+1-len(keys)]
            else: next_key = keys[curr_key-1]
            self._enter_building_mode(BUILDING_TYPES[next_key])

    def _rotate_terraform(self):
        if self.cast_terraform is None: return False
        self.tilemap.untie_from_cursor()
        self.cast_terraform.rotate(1)
        self.tilemap.tie_to_cursor(self.cast_terraform.setup(self.tiles))
        return True

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        if self.cursor_can_move:
            if self.q_pressed and not self.d_pressed:
                self.tilemap.move_cursor(5)
            elif self.d_pressed and not self.q_pressed:
                self.tilemap.move_cursor(2)
            if self.w_pressed and not self.s_pressed:
                self.tilemap.move_cursor(0)
            elif self.s_pressed and not self.w_pressed:
                self.tilemap.move_cursor(3)
            if self.e_pressed and not self.a_pressed:
                self.tilemap.move_cursor(1)
            elif self.a_pressed and not self.e_pressed:
                self.tilemap.move_cursor(4)
            self.cursor_can_move = False
        else:
            self.cursor_timer += 1
            if self.cursor_timer >= CURSOR_SPEED:
                self.cursor_can_move = True
                self.cursor_timer = 0
                
        if self.up_pressed and not self.down_pressed:
            self.tilemap.move_camera(Vec2(0, 1))
        elif self.down_pressed and not self.up_pressed:
            self.tilemap.move_camera(Vec2(0, -1))
        if self.left_pressed and not self.right_pressed:
            self.tilemap.move_camera(Vec2(-1, 0))
        elif self.right_pressed and not self.left_pressed:
            self.tilemap.move_camera(Vec2(1, 0))

        self.tilemap.update()
        

def main():
    game = Game(RESOLUTION, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == '__main__':
    main()
