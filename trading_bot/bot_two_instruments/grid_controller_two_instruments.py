from trading_bot.base_grid_controller import BaseGridController
from copy import deepcopy

from utils import load_config, to_utc_timestamp
from constants import *

config = load_config('config.yaml')


class GridControllerTwoInstruments(BaseGridController):
    def __init__(self, ndigits_rounding: int):
        super().__init__(ndigits_rounding=ndigits_rounding)

        # self.active_limit_orders = {}
        # hash(instr1_limit, instr2_limit) -> order info
        self.pending_limit_orders = {}
        self.pending_take_profit_orders = {}
        self.limit_to_take_profit_orders = {}  # limit -> take profit
        self.take_profit_to_limit_orders = {}  # take profit -> limit

    def get_pending_limit_orders(self):
        return deepcopy(list(self.pending_limit_orders))

    def get_pending_take_profit_orders(self):
        return deepcopy(list(self.pending_take_profit_orders))
