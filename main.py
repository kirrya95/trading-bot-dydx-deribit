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

    # instrument_name = f'{instr1}-{instr2}'
    # instrument_name = (instr1 if instr2 == '-' else instrument_name)
    # print(instrument_name)

    # loop = asyncio.get_event_loop()

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
    instr1 = config['trading_parameters']['instrument_1']
    instr2 = config['trading_parameters']['instrument_2']
    trading_bot = TradingBot(
        # number_of_instruments=1,
        conn=deribit_connection,
        telegram_bot=telegram_notifier,
    )

    # await deribit_connection.subscribe_to_order_updates()
    # tasks = []
    if instr2 == '-':
        await (trading_bot.run_bot_one_instrument(
            instrument_name=instr1))
    else:
        await (trading_bot.run_bot_two_instruments(
            instr1=instr1, instr2=instr2))

    # tasks.append(deribit_connection.start_listening())

    # print(await deribit_connection.get_all_orders())

    print('here')

    # await asyncio.gather(*tasks)

    # trading_bot.run_deribit_bot()

    # req1 = trading_bot.dydx_conn1.get_req_for_websocket()
    # async with websockets.connect('wss://api.stage.dydx.exchange/v3/ws') as websocket:

    #     await websocket.send(json.dumps(req1))
    #     print(f'> {req1}')

    #     while True:
    #         res = await websocket.recv()
    #         print(f'< {res}')
    #         print('-----------------------\n')


# asyncio.get_event_loop().run_until_complete(main())
if __name__ == '__main__':
    asyncio.run(main())
