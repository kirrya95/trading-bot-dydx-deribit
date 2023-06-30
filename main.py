import requests
import json
import time
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

    dydx_connection = dYdXConnection(config=config)


    # print(result)

    print(dydx_connection.get_index_price())

    telegram_notifier = TelegramNotifier(
        bot_token=config['telegram']['bot_token'],
        chat_id=config['telegram']['chat_id']
    )

    trading_bot = TradingBot(dydx_connection, telegram_notifier, config)
    await trading_bot.run()



asyncio.run(main())
