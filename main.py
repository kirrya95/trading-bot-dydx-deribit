import requests
import json
import websockets
from datetime import datetime
import asyncio

from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import MARKET_ETH_USD, MARKET_BTC_USD

from connectors import dYdXConnection, DeribitConnection
from telegram_bot import TelegramNotifier

from trading_bot.trading_bot import TradingBot

from utils import load_config

config = load_config('config.yaml')


async def main():
    # dydx_connection1 = dYdXConnection(
    #     instrument=config['trading_parameters']['instrument_1'], config=config)

    # dydx_connection2 = dYdXConnection(
    #     instrument=config['trading_parameters']['instrument_2'], config=config)

    deribit_connection1 = DeribitConnection(
        client_id=config['credentials']['deribit']['client_id'],
        client_secret=config['credentials']['deribit']['client_secret']
    )

    telegram_notifier = TelegramNotifier(
        bot_token=config['telegram']['bot_token'],
        chat_id=config['telegram']['chat_id']
    )

    # print(await deribit_connection1.cancel_all_orders())

    await deribit_connection1.connect()  # инициализация соединения
    await deribit_connection1.authenticate()  # аутентификация
    # отмена всех ордеров
    await deribit_connection1.cancel_all_orders(instrument_name='BTC-PERPETUAL')

    # print(await deribit_connection1.get_asset_price(
    #     instrument_name='BTC-PERPETUAL'))

    # print(await deribit_connection1.get_contract_size(
    #     instrument_name='BTC-PERPETUAL'))

    # print(await deribit_connection1.create_limit_order(
    #     instrument_name='BTC-PERPETUAL', amount=10, price=10000, action='buy'))

    # trading_bot = TradingBot(
    #     deribit_connection1, deribit_connection1, telegram_notifier, config)
    # await trading_bot.run()

    # trading_bot.run_deribit_bot()

    # req1 = trading_bot.dydx_conn1.get_req_for_websocket()
    # async with websockets.connect('wss://api.stage.dydx.exchange/v3/ws') as websocket:

    #     await websocket.send(json.dumps(req1))
    #     print(f'> {req1}')

    #     while True:
    #         res = await websocket.recv()
    #         print(f'< {res}')
    #         print('-----------------------\n')


# asyncio.run(main())

asyncio.get_event_loop().run_until_complete(main())
