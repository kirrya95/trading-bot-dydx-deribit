from copy import deepcopy

from utils import load_config, to_utc_timestamp
from utils.error_checkers import check_grid_direction
from constants import *

config = load_config('config.yaml')


class BaseGridController:
    def __init__(self, ndigits_rounding: int):
        self.grid_step = config['trading_parameters']['grid_step']
        self.grid_ndigits_rounding = ndigits_rounding
        self.instr_price = None
        self.grid_size = None
        self.direction = None
        self.current_grid = None

    @check_grid_direction
    async def initialize_grid(self, instr_price: float, grid_size: int, grid_direction: str):
        if grid_direction not in [GridDirections.GRID_DIRECTION_LONG, GridDirections.GRID_DIRECTION_SHORT]:
            raise ValueError(
                f'Incorrect side. Should be either {GridDirections.GRID_DIRECTION_LONG} or {GridDirections.GRID_DIRECTION_SHORT}')

        self.grid_step = config['trading_parameters']['grid_step']
        self.instr_price = instr_price
        self.grid_size = grid_size
        self.direction = grid_direction
        self.current_grid = None
        if grid_direction == GridDirections.GRID_DIRECTION_LONG:
            self.current_grid = [round(instr_price - self.grid_step * i, ndigits=self.grid_ndigits_rounding)
                                 for i in range(1, grid_size + 1)]
        elif grid_direction == GridDirections.GRID_DIRECTION_SHORT:
            self.current_grid = [round(instr_price + self.grid_step * i, ndigits=self.grid_ndigits_rounding)
                                 for i in range(1, grid_size + 1)]

    async def change_grid_size(self, delta: int):
        self.grid_size += delta
        await self.initialize_grid(
            instr_price=self.instr_price, grid_size=self.grid_size, grid_direction=self.direction)

    ### GETTERS ###

    async def get_grid(self):
        return self.current_grid

    async def get_grid_size(self):
        return self.grid_size
