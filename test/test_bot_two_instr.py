import pytest
import typing as tp
import time
import asyncio

from utils import *

# from trading_bot.bot_two_instruments.grid_controller_two_instruments import GridControllerTwoInstruments
from trading_bot.bot_two_instruments.bot_limit import TradingBotTwoInstrumentsLimitOrders

from constants import GridDirections


@pytest.fixture
def fixture_bot():
    bot = TradingBotTwoInstrumentsLimitOrders()
    return bot


@pytest.mark.asyncio
async def test_create_batch_limit_order(fixture_bot):
    instr1_amount = 0.1
    instr2_amount = 0.1
    prices_instr1 = {'bid': 100.0, 'ask': 100.1}
    prices_instr2 = {'bid': 100.0, 'ask': 100.1}
    instr1_side = 'buy'
    instr2_side = 'sell'

    await fixture_bot.create_batch_limit_order(instr1_amount, instr2_amount, prices_instr1, prices_instr2, instr1_side, instr2_side)

    assert False
