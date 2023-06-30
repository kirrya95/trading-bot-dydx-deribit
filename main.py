import requests
import json
import time
from datetime import datetime
import asyncio


from dydx import dYdXConnection
from telegram_bot import TelegramNotifier
from trading_bot.trading_bot import TradingBot

from utils import load_config


config = load_config('config.yml')


async def main():

    # print(config.get('stark_private_key', None))

    dydx_connection = dYdXConnection(config=config)
    # dydx_host=config['platforms']['dydx_testnet']['host'],
    # api_key_credentials=config['api_key_credentials'],
    # stark_private_key=config.get('stark_private_key', None)

    print(dydx_connection.test())

    # telegram_notifier = TelegramNotifier(
    #     bot_token=config['telegram']['bot_token'],
    #     chat_id=config['telegram']['chat_id']
    # )

    # trading_bot = TradingBot(dydx_connection, telegram_notifier, config['config'])
    # trading_bot.run()

    # await telegram_notifier.send_message(message="Hello, World!")


asyncio.run(main())


# main()
