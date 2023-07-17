from copy import deepcopy

from utils import load_config, to_utc_timestamp
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

    ### GETTERS ###

    async def get_grid(self):
        return self.current_grid

    async def get_grid_size(self):
        return self.grid_size
