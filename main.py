import requests
import json
from datetime import datetime
import asyncio

from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import MARKET_ETH_USD, MARKET_BTC_USD

from dydx import dYdXConnection
from telegram_bot import TelegramNotifier
from trading_bot.trading_bot import TradingBot

from utils import load_config

config = load_config('config.yml')


async def main():

    dydx_connection1 = dYdXConnection(
        instrument=config['trading_parameters']['instrument_1'], config=config)

    dydx_connection2 = dYdXConnection(
        instrument=config['trading_parameters']['instrument_2'], config=config)

    telegram_notifier = TelegramNotifier(
        bot_token=config['telegram']['bot_token'],
        chat_id=config['telegram']['chat_id']
    )

    trading_bot = TradingBot(
        dydx_connection1, dydx_connection2, telegram_notifier, config)
    await trading_bot.run()


asyncio.run(main())
