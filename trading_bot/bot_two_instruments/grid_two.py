from trading_bot.base_grid_controller import BaseGridController
from copy import deepcopy

from utils import load_config, to_utc_timestamp
from constants import *

config = load_config('config.yaml')


class GridControllerTwoInstruments(BaseGridController):
    def __init__(self, ndigits_rounding: int):
        super().__init__(ndigits_rounding=ndigits_rounding)

        self.grid = {}
        self.pending_limit_orders = {}
        self.pending_take_profit_orders = {}
        self.limit_to_take_profit_orders = {}  # limit -> take profit
        self.take_profit_to_limit_orders = {}  # take profit -> limit

    async def initialize_grid(self, instr_price: float, grid_size: int, grid_direction: str):
        ndigits_rounding = 8
        for i in range(grid_size):
            level = round(instr_price + self.grid_step *
                          (1+i), ndigits=ndigits_rounding)
            self.grid[i] = {"level": level, "reached": False}




