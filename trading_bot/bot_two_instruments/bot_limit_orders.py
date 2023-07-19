import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from .base_bot_two_instruments import BaseTradingBotTwoInstruments


config = load_config('config.yaml')


class TradingBotTwoInstrumentsLimitOrders(BaseTradingBotTwoInstruments):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.instr1_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr1_name]
        self.instr2_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr2_name]

    async def check_limit_orders_are_fullfilled(self, limit_order_id) -> bool:
        pass

    async def check_take_profit_orders_are_fullfilled(self, take_profit_order_id) -> bool:
        pass

    async def run(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr_name, kind=self.kind)
