import pytest
import typing as tp
import time
import asyncio

from utils import *

# from trading_bot.bot_two_instruments.grid_controller_two_instruments import GridControllerTwoInstruments
from trading_bot.bot_two_instruments.grid_two import GridControllerTwoInstruments

from constants import GridDirections

config = load_config('config.yaml')


@pytest.fixture
def grid_controller():
    controller = GridControllerTwoInstruments(ndigits_rounding=8)
    controller.grid_step = 0.1  # Set a sample grid step
    return controller


@pytest.mark.asyncio
async def test_initialize_grid(grid_controller):
    spread_price = 100.0
    grid_size = 5
    grid_direction = GridDirections.GRID_DIRECTION_LONG

    # grid = grid_controller
    print('123')

    grid_controller.initialize_grid(spread_price, grid_size, grid_direction)
    print(grid_controller.grid)

    expected_levels = [100.1, 100.2, 100.3, 100.4, 100.5]
    for i, level_info in grid_controller.grid.items():
        print(level_info.reached)
        # assert level_info["level"] == expected_levels[i]
        # assert not level_info["reached"]


@pytest.mark.asyncio
async def test_grid_overflow(grid_controller):
    instr_price = 100.0
    grid_size = 5
    grid_direction = GridDirections.GRID_DIRECTION_LONG


@pytest.mark.asyncio
async def test_update_take_profit(grid_controller):
    spread_price = 100.0
    grid_size = 5
    grid_direction = GridDirections.GRID_DIRECTION_LONG

    # grid = grid_controller
    print('123')

    grid_controller.initialize_grid(spread_price, grid_size, grid_direction)
    # print(grid_controller.grid)

    order1_id = 1
    order2_id = 2

    grid_controller.update_limit_order(
        level=99.7, order1_id=order1_id, order2_id=order2_id)

    assert grid_controller.grid[99.7].limit_order_hash == hash(
        (order1_id, order2_id))
    print(grid_controller.grid[99.7])
