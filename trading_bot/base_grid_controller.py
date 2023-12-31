from copy import deepcopy

from utils import load_config, to_utc_timestamp
from utils.error_checkers import check_grid_direction
from constants import *

config = load_config('config.yaml')


class BaseGridController:
    def __init__(self):
        self.grid_step = config['trading_parameters']['grid_step']
        self.grid_ndigits_rounding = config['trading_parameters']['grid_ndigits_rounding']
        self.instr_price = None
        # self.grid_size = config['trading_parameters']['grid_size']
        self.grid_direction = None
        # self.initial_grid = None

    # @check_grid_direction
    # async def initialize_grid(self, instr_price: float, grid_size: int, grid_direction: str):
    #     self.grid_step = config['trading_parameters']['grid_step']
    #     self.instr_price = instr_price
    #     self.grid_size = grid_size
    #     self.grid_direction = grid_direction
    #     # self.initial_grid = None
    #     # self.last_achieved_level = instr_price
    #     # print('last_achieved_level', self.last_achieved_level)
    #     if grid_direction == GridDirections.GRID_DIRECTION_LONG:
    #         self.initial_grid = [round(instr_price - self.grid_step * i, ndigits=self.grid_ndigits_rounding)
    #                              for i in range(1, grid_size + 1)]
    #     elif grid_direction == GridDirections.GRID_DIRECTION_SHORT:
    #         self.initial_grid = [round(instr_price + self.grid_step * i, ndigits=self.grid_ndigits_rounding)
    #                              for i in range(1, grid_size + 1)]

    # async def change_grid_size(self, delta: int):
    #     self.grid_size += delta
    #     await self.initialize_grid(
    #         instr_price=self.instr_price, grid_size=self.grid_size, grid_direction=self.grid_direction)

    # ### GETTERS ###

    # def get_grid(self):
    #     return self.initial_grid

    # def get_grid_size(self):
    #     return self.grid_size
