import requests
import json
import websockets
from datetime import datetime
import asyncio

from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import MARKET_ETH_USD, MARKET_BTC_USD

from connectors import dYdXConnection, DeribitConnection
from telegram_bot import TelegramNotifier

# from trading_bot.trading_bot import TradingBot

from trading_bot import TradingBotOneInstrumentMarketOrders, TradingBotTwoInstrumentsMarketOrders

from utils import load_config

config = load_config('config.yaml')


async def main():
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
    if instr2 != '-':
        trading_bot = TradingBotTwoInstrumentsMarketOrders(
            conn=deribit_connection,
            telegram_bot=telegram_notifier,
        )
    else:
        trading_bot = TradingBotOneInstrumentMarketOrders(
            conn=deribit_connection,
            telegram_bot=telegram_notifier,
        )
    try:
        await asyncio.gather(
            trading_bot.run(),
            trading_bot.send_strategy_info())
    except Exception as e:
        print(e)
        await telegram_notifier.send_message(f'Exception: {e}', parse_mode='')
        await asyncio.sleep(1)
        await telegram_notifier.send_message('Bot closed')
        return

    print('trading bot closed')


if __name__ == '__main__':
    asyncio.run(main())
