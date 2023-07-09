import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

# from trading_bot.base_bot import BaseTradingBot

from trading_bot.bot_one_instrument import BaseTradingBotOneInstrument


config = load_config('config.yaml')


class TradingBotOneInstrumentLimitOrders(BaseTradingBotOneInstrument):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)
    
    

    async def run(self):
        # no need to divide by 2
        # amount_usdc_to_have = config['trading_parameters']['start_deposit']
        amount_usdc_to_have = 0  # we don't have to have any amount of asset at the start
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        # tidy asset amount
        await self.tidy_instrument_amount(instrument_name=self.instr_name, amount_in_usdc_to_have=amount_usdc_to_have)
        self.initial_instr_price = await self.get_instrument_price()
        self.initial_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)

        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price()
                self.current_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)

                local_grid = await self.calculate_local_grid()
                print('instrument price:', self.current_instr_price)
                print('local grid:', local_grid)
                print('take profit spreads:', self.take_profit_asset_prices)
