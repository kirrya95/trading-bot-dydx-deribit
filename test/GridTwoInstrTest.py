from trading_bot.bot_two_instruments.grid_controller_two_instruments import GridControllerTwoInstruments
import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils.error_checkers import check_grid_direction

from utils import *
from constants import *


config = load_config('config.yaml')


async def testCorrectInitialization():
    print('test 1')
    grid_ndigits_rounding = 8
    initial_spread_price = 0.064123
    orders_in_market = 10
    grid_direction = GridDirections.GRID_DIRECTION_LONG

    grid_controller = GridControllerTwoInstruments(
        ndigits_rounding=grid_ndigits_rounding)

    await grid_controller.initialize_grid(instr_price=initial_spread_price,
                                          grid_size=orders_in_market,
                                          grid_direction=grid_direction)

    print(grid_controller.current_grid)

    last_achieved_level = grid_controller.current_grid[0]

    await grid_controller.update_last_achieved_level(last_achieved_level)

    print(grid_controller.current_grid)

    last_achieved_level = grid_controller.current_grid[0]

    await grid_controller.update_last_achieved_level(last_achieved_level)

    print(grid_controller.current_grid)


async def runTests():
    await testCorrectInitialization()

# if __name__ == '__main__':
#     asyncio.run(main)
