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

    # expected_levels = [100.1, 100.2, 100.3, 100.4, 100.5]
    expected_levels = [99.9, 99.8, 99.7, 99.6, 99.5]
    for i, level, in enumerate(grid_controller.grid.keys()):
        print(i, level)
        assert level == expected_levels[i]
        assert not grid_controller.grid[level].reached


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

    grid_controller.initialize_grid(spread_price, grid_size, grid_direction)
    # print(grid_controller.grid)

    limit_order1_id = 1
    limit_order2_id = 2

    level = 99.7

    grid_controller.update_limit_order(
        level=level, order1_id=limit_order1_id, order2_id=limit_order2_id)

    assert grid_controller.grid[level].limit_order_hash == hash(
        (limit_order1_id, limit_order2_id))

    take_profit_order1_id = 3
    take_profit_order2_id = 4

    grid_controller.update_take_profit_order(
        level=level, order1_id=take_profit_order1_id, order2_id=take_profit_order2_id)
    print(grid_controller.grid[level])

    # should raise because already take profit exists
    with pytest.raises(Exception):
        _take_profit_order1_id = take_profit_order1_id + 1
        grid_controller.update_take_profit_order(
            level=level, order1_id=_take_profit_order1_id, order2_id=take_profit_order2_id)

    # level that not exits
    with pytest.raises(KeyError):
        _level = level + grid_controller.grid_step * 1000
        grid_controller.update_limit_order(
            level=_level, order1_id=limit_order1_id, order2_id=limit_order2_id)

    print(take_profit_order1_id)


@pytest.mark.asyncio
async def test_running_window(grid_controller):
    # should not add new orders if exceeded max amount
    pass
