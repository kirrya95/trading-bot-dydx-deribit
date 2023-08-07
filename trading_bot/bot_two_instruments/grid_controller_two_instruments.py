from trading_bot.base_grid_controller import BaseGridController
import typing as tp
from copy import deepcopy
from dataclasses import dataclass

from utils import load_config, to_utc_timestamp
from utils.error_checkers import check_grid_direction

from constants import *

config = load_config('config.yaml')


@dataclass
class GridEntry:
    reached: bool
    take_profit_level: float
    limit_order_hash: tp.Union[str, None]
    take_profit_order_hash: tp.Union[str, None]


class GridControllerTwoInstruments(BaseGridController):
    def __init__(self):
        super().__init__()

        # TODO: change this
        # for two instruments, we don't need 'orders_in_market' parameter
        # self.orders_in_market = 5
        self.max_orders_amount = config['trading_parameters']['max_orders_amount']
        self.grid: dict[int, GridEntry] = {}
        # warning: this dict potentially can be very large
        self.hash_to_orders = {}

    def initialize_grid(self, spread_price: float, grid_direction: str):
        grid_size = self.max_orders_amount
        level: float
        take_profit_level: float
        for i in range(grid_size):
            if grid_direction == GridDirections.GRID_DIRECTION_LONG:
                level = round(spread_price - self.grid_step *
                              (1+i), ndigits=self.grid_ndigits_rounding)
                take_profit_level = level + self.grid_step
            else:
                level = round(spread_price + self.grid_step *
                              (1+i), ndigits=self.grid_ndigits_rounding)
                take_profit_level = level - self.grid_step

            self.grid[level] = GridEntry(
                take_profit_level=take_profit_level,
                reached=False,
                limit_order_hash=None,
                take_profit_order_hash=None
            )

    def clear_level(self, level: float):
        # clearing in this way, we ensure having error if GridEntry attributes are changed
        self.grid[level] = GridEntry(
            take_profit_level=self.grid[level].take_profit_level,
            reached=False,
            limit_order_hash=None,
            take_profit_order_hash=None
        )

    def update_limit_order(self, level: float, order1_id: int, order2_id: int):
        # check that 'reached' attr is False, and limit order hash is None
        self._check_limitOrder(level)

        self.grid[level].limit_order_hash = self.calculate_hash(
            order1_id, order2_id)
        self.hash_to_orders[self.grid[level].limit_order_hash] = (
            order1_id, order2_id)
        self.grid[level].reached = True

    def update_take_profit_order(self, level: float, order1_id: int, order2_id: int):
        # check if level is reached and limit order hash is not None
        self._check_takeProfitOrder(level)

        take_profit_hash = self.calculate_hash(order1_id, order2_id)
        self.grid[level].take_profit_order_hash = take_profit_hash
        self.hash_to_orders[take_profit_hash] = (order1_id, order2_id)

    @staticmethod
    def calculate_hash(order1_id: int, order2_id: int):
        return hash((order1_id, order2_id))

    ### checkers ###

    def _check_limitOrder(self, level: float):
        if self.grid[level].reached is True:
            raise Exception(
                f'Level {level} is already reached!')
        if self.grid[level].limit_order_hash is not None:
            raise Exception(
                f'Limit order hash is not None for level {level}!')

    def _check_takeProfitOrder(self, level: float):
        if self.grid[level].reached is False:
            raise Exception(
                f'Level {level} is not reached!')
        if self.grid[level].limit_order_hash is None:
            raise Exception(
                f'Limit order hash is None for level {level}!')
        if self.grid[level].take_profit_order_hash is not None:
            raise Exception(
                f'Take profit order hash is not None for level {level}!')

    def _check_gridSizeNotExceeded(self):
        if len(self.grid) >= self.max_orders_amount:
            raise Exception(
                f'Grid size exceeded! Current grid size: {len(self.grid)}')
