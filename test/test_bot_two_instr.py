import pytest
import typing as tp
import time
import asyncio

from utils import *

# from trading_bot.bot_two_instruments.grid_controller_two_instruments import GridControllerTwoInstruments
from trading_bot.bot_two_instruments.bot_limit import TradingBotTwoInstrumentsLimitOrders

from constants import GridDirections

from connectors import DeribitConnection
from telegram_bot import TelegramNotifier

config = load_config('config.yaml')

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
async def fixture_bot():
    deribit_connection = DeribitConnection(
        client_id=config['credentials']['deribit']['client_id'],
        client_secret=config['credentials']['deribit']['client_secret']
    )
    await deribit_connection.connect()
    await deribit_connection.authenticate()

    telegram_notifier = TelegramNotifier(
        bot_token=config['telegram']['bot_token'],
        chat_id=config['telegram']['chat_id']
    )
    trading_bot = TradingBotTwoInstrumentsLimitOrders(
        conn=deribit_connection,
        telegram_bot=telegram_notifier,
    )
    return trading_bot


@pytest.mark.asyncio()
async def test_create_batch_limit_order(fixture_bot):
    instr1_amount = 0.1
    instr2_amount = 0.1
    prices_instr1 = {'bid': 100.0, 'ask': 100.1}
    prices_instr2 = {'bid': 100.0, 'ask': 100.1}
    instr1_side = 'buy'
    instr2_side = 'sell'

    bot = await (fixture_bot)

    # await fixture_bot.create_batch_limit_order(instr1_amount, instr2_amount, prices_instr1, prices_instr2, instr1_side, instr2_side)

    await (bot.run())

    await bot.conn.connection.close()

    print('bot.grid_controller.grid')
    print(bot.grid_controller.grid)
