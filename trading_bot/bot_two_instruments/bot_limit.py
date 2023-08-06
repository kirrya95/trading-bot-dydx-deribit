import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils.error_checkers import check_grid_direction

from utils import *
from constants import *

from .base_bot_two_instruments import BaseTradingBotTwoInstruments
from .grid_controller_two_instruments import GridControllerTwoInstruments


config = load_config('config.yaml')


class TradingBotTwoInstrumentsLimitOrders(BaseTradingBotTwoInstruments):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.instr1_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr1_name]
        self.instr2_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr2_name]

        # TODO: make it configurable
        grid_ndigits_rounding = 8

        self.grid_controller = GridControllerTwoInstruments(
            ndigits_rounding=grid_ndigits_rounding)

    async def check_limit_orders_are_fullfilled(self, limit_orders_hash) -> bool:
        pass

    async def check_take_profit_orders_are_fullfilled(self, take_profit_orders_hash) -> bool:
        pass

    async def handle_two_limit_orders_executions(self):
        pass

    async def create_batch_limit_order(self,
                                       instr1_amount, instr2_amount,
                                       prices_instr1, prices_instr2,
                                       instr1_side, instr2_side):
        pass

    async def get_instr_prices_and_spread(self):
        # current_prices_instr1 = await self.conn.get_asset_price(instrument_name=self.instr1_name)
        # current_prices_instr2 = await self.conn.get_asset_price(instrument_name=self.instr2_name)

        # current_spread_price = await self.get_spread_price_from_two_instr_prices(instr1_prices=current_prices_instr1,
        #                                                                          instr2_prices=current_prices_instr2,
        #                                                                          grid_direction=self.anti_grid_direction)
        # return (current_prices_instr1, current_prices_instr2, current_spread_price)
        pass

    async def run(self):
        pass


if __name__ == '__main__':
    pass
