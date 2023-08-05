# from unittest.mock import AsyncMock
# import unittest
# # from trading_bot.bot_two_instruments.grid_controller_two_instruments import GridControllerTwoInstruments
# import typing as tp
# import time
# import asyncio

# from telegram_bot import TelegramNotifier
# from connectors import dYdXConnection, DeribitConnection
# from utils.error_checkers import check_grid_direction

# from utils import *
# from constants import *

# from trading_bot.bot_two_instruments.grid_two import GridControllerTwoInstruments


# config = load_config('config.yaml')


# class TestGridControllerTwoInstruments(unittest.TestCase):
#     def setUp(self):
#         self.controller = GridControllerTwoInstruments(ndigits_rounding=8)
#         self.controller.grid_step = 0.1  # Set a sample grid step

#     def test_initialize_grid(self):
#         instr_price = 100.0
#         grid_size = 5
#         grid_direction = "up"

#         self.controller.initialize_grid(instr_price, grid_size, grid_direction)

#         expected_levels = [100.1, 100.2, 100.3, 100.4, 100.5]
#         for i, level_info in self.controller.grid.items():
#             print(self.controller.grid)

#             self.assertEqual(level_info["level"], expected_levels[i])
#             self.assertFalse(level_info["reached"])

#     # You can add more test cases here


# unittest.main()
