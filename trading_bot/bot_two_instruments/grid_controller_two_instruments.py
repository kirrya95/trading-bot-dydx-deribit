from trading_bot.base_grid_controller import BaseGridController
from copy import deepcopy

from utils import load_config, to_utc_timestamp
from constants import *

config = load_config('config.yaml')


class GridControllerTwoInstruments(BaseGridController):
    def __init__(self, ndigits_rounding: int):
        super().__init__(ndigits_rounding=ndigits_rounding)

        self.last_achieved_level = None
        self.pending_limit_orders = {}
        self.pending_take_profit_orders = {}
        self.limit_to_take_profit_orders = {}  # limit -> take profit
        self.take_profit_to_limit_orders = {}  # take profit -> limit

    async def update_last_achieved_level(self, level: float):
        self.last_achieved_level = level

    async def update_pending_limit_order_info(self, instr1_order_id: str, instr1_order_info: dict,
                                              instr2_order_id: str, instr2_order_info: dict):
        key = await self.get_orders_hash(instr1_order_id, instr2_order_id)
        self.pending_limit_orders[key][instr1_order_id] = instr1_order_info
        self.pending_limit_orders[key][instr2_order_id] = instr2_order_info

    async def del_pending_limit_order_info(self, instr1_order_id: str, instr2_order_id: str):
        key = await self.get_orders_hash(instr1_order_id, instr2_order_id)
        self.pending_limit_orders[key].pop(instr1_order_id)
        self.pending_limit_orders[key].pop(instr2_order_id)
        if not self.pending_limit_orders[key]:
            self.pending_limit_orders.pop(key)

    async def update_pending_take_profit_order_info(self, instr1_order_id: str, instr1_order_info: dict,
                                                    instr2_order_id: str, instr2_order_info: dict):
        key = hash((instr1_order_id, instr2_order_id))
        self.pending_take_profit_orders[key][instr1_order_id] = instr1_order_info
        self.pending_take_profit_orders[key][instr2_order_id] = instr2_order_info

    async def del_pending_take_profit_order_info(self, instr1_order_id: str, instr2_order_id: str):
        key = await self.get_orders_hash(instr1_order_id, instr2_order_id)
        self.pending_take_profit_orders[key].pop(instr1_order_id)
        self.pending_take_profit_orders[key].pop(instr2_order_id)
        if not self.pending_take_profit_orders[key]:
            self.pending_take_profit_orders.pop(key)

    ### GETTERS ###

    async def get_filtered_grid(self):
        index_of_last_achieved_level = self.current_grid.index(
            self.last_achieved_level)
        return self.current_grid[index_of_last_achieved_level + 1:]

    async def get_pending_limit_orders(self):
        return deepcopy(list(self.pending_limit_orders.keys()))

    async def get_pending_take_profit_orders(self):
        return deepcopy(list(self.pending_take_profit_orders.keys()))

    async def get_limit_orders_ids(self):
        return deepcopy(list(self.limit_to_take_profit_orders.keys()))

    async def get_take_profit_orders_ids(self):
        return deepcopy(list(self.take_profit_to_limit_orders.keys()))

    ### UTILS ###

    async def get_orders_hash(self, instr1_limit, instr2_limit):
        return hash((instr1_limit, instr2_limit))
