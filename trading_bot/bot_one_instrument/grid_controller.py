from abc import ABC, abstractmethod
from copy import deepcopy

from utils import load_config, to_utc_timestamp
from constants import *

config = load_config('config.yaml')


class GridController(ABC):
    def __init__(self, ndigits_rounding: int):
        self.grid_step = config['trading_parameters']['grid_step']
        self.grid_ndigits_rounding = ndigits_rounding
        self.instr_price = None
        self.grid_size = None
        self.direction = None
        self.current_grid = None

        self.active_limit_orders = {}
        self.take_profit_orders = {}
        self.limit_to_take_profit_orders = {}  # limit -> take profit
        self.take_profit_to_limit_orders = {}  # take profit -> limit

    async def initialize_grid(self, instr_price: float, grid_size: int, grid_direction: str):
        if grid_direction not in [GRID_DIRECTION_LONG, GRID_DIRECTION_SHORT]:
            raise ValueError(
                f'Incorrect side. Should be either {GRID_DIRECTION_LONG} or {GRID_DIRECTION_SHORT}')

        self.grid_step = config['trading_parameters']['grid_step']
        self.instr_price = instr_price
        self.grid_size = grid_size
        self.direction = grid_direction
        self.current_grid = None
        if grid_direction == GRID_DIRECTION_LONG:
            self.current_grid = [round(instr_price + self.grid_step * i, ndigits=self.grid_ndigits_rounding)
                                 for i in range(1, grid_size + 1)]
        elif grid_direction == GRID_DIRECTION_SHORT:
            self.current_grid = [round(instr_price - self.grid_step * i, ndigits=self.grid_ndigits_rounding)
                                 for i in range(1, grid_size + 1)]

    # async def fill_grid_with_orders(self):
    #     for i in range(self.grid_size):
    #         await self.create_limit_order(
    #             price=self.current_grid[i], amount=self.amount)

    async def update_active_order_info(self, order_id: str, order_info: dict):
        self.active_limit_orders[order_id] = order_info

    async def link_take_profit_order(self, take_profit_order_id: str, limit_order_id: str):
        self.limit_to_take_profit_orders[limit_order_id
                                         ] = take_profit_order_id
        self.take_profit_to_limit_orders[take_profit_order_id
                                         ] = limit_order_id

    async def update_grid_size(self, delta: int):
        self.grid_size += delta
        await self.initialize_grid(
            instr_price=self.instr_price, grid_size=self.grid_size, grid_direction=self.direction)
        # if delta > 0:
        #     for i in range(delta):
        #         if self.direction == GRID_DIRECTION_LONG:
        #             self.grid.append(self.grid[-1] + self.grid_step)
        #         elif self.direction == GRID_DIRECTION_SHORT:
        #             self.grid.append(self.grid[-1] - self.grid_step)
        # elif delta < 0:
        #     for _ in range(abs(delta)):
        #         self.grid.pop()

    async def remove_limit_order(self, order_id: str):
        try:
            take_profit_order_id = self.limit_to_take_profit_orders.get(
                order_id)
            self.take_profit_to_limit_orders.pop(take_profit_order_id)
        except KeyError:
            pass
        self.limit_to_take_profit_orders.pop(order_id)
        self.active_limit_orders.pop(order_id)

    async def remove_take_profit_order(self, order_id: str):
        try:
            limit_order_id = self.take_profit_to_limit_orders.get(order_id)
            self.limit_to_take_profit_orders.pop(limit_order_id)
        except KeyError:
            pass
        self.take_profit_to_limit_orders.pop(order_id)
        self.take_profit_orders.pop(order_id)

    ### GETTERS ###

    async def get_grid(self):
        return self.current_grid

    async def get_grid_size(self):
        return self.grid_size

    async def get_active_limit_orders_ids(self):
        return deepcopy(self.active_limit_orders.keys())

    async def get_take_profit_orders_ids(self):
        return deepcopy(self.take_profit_orders.keys())

    async def get_active_limit_order_info(self, order_id: str):
        return self.active_limit_orders[order_id]

    async def get_linked_limit_orders_ids(self):
        """
        Description:
            Returns list of limit orders ids that are linked to take profit orders.
        """
        return deepcopy(self.limit_to_take_profit_orders.keys())

    async def get_linked_take_profit_orders_ids(self):
        """
        Description:
            Returns list of take profit orders ids that are linked to limit orders.
        """
        return deepcopy(self.take_profit_to_limit_orders.keys())

    async def get_limit_order_id_by_take_profit_order_id(self, take_profit_order_id: str):
        """
        Description:
            Returns limit order id that is linked to take profit order.
        """
        return self.take_profit_to_limit_orders[take_profit_order_id]
