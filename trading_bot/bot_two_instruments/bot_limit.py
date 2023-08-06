import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
# from utils.error_checkers import check_grid_direction

from constants import *

from .base_bot_two_instruments import BaseTradingBotTwoInstruments
# from .grid_controller_two_instruments import GridControllerTwoInstruments

from .grid_two import GridControllerTwoInstruments, GridEntry

import utils

config = utils.load_config('config.yaml')


class TradingBotTwoInstrumentsLimitOrders(BaseTradingBotTwoInstruments):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        # we store here because here we create limit orders
        self.instr1_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr1_name]
        self.instr2_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr2_name]

        self.grid_controller = GridControllerTwoInstruments()

    async def check_limit_orders_are_fullfilled(self, order1_id, order2_id) -> bool:
        pass
        return False

    async def check_take_profit_orders_are_fullfilled(self, order1_id, order2_id) -> bool:
        pass
        return False

    async def handle_two_limit_orders_executions(self):
        pass

    async def create_batch_limit_order(self,
                                       instr1_amount, instr2_amount,
                                       prices_instr1, prices_instr2,
                                       instr1_side, instr2_side):
        pass

    async def get_instr_prices_and_spread(self) -> tp.Tuple[utils.InstrPrices, utils.InstrPrices, float]:
        prices_instr1 = utils.InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr1_name)))
        prices_instr2 = utils.InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr2_name)))

        spread_price = utils.calculate_spread_from_two_instr_prices(instr1_bid_ask=prices_instr1,
                                                                    instr2_bid_ask=prices_instr2,
                                                                    grid_direction=self.anti_grid_direction,
                                                                    spread_operator=self.spread_operator)
        return (prices_instr1, prices_instr2, spread_price)

    async def _prepare(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr1_name, kind=self.kind1)
        await self.conn.cancel_all_orders(instrument_name=self.instr2_name, kind=self.kind2)

        (_, _, spread_price) = await self.get_instr_prices_and_spread()

        print()
        print(spread_price)

        self.grid_controller.initialize_grid(
            spread_price=spread_price, grid_direction=self.grid_direction)

    async def run(self):
        await self._prepare()

        while True:
            async with self.lock:
                # check total take profit. If reached, then bot stops running
                await self.check_total_take_profit()
                break

                (instr1_bid_ask, instr2_bid_ask, spread_price) = await self.get_instr_prices_and_spread()

                # if self.grid_direction == GridDirections.GRID_DIRECTION_LONG:
                #     for (level, level_info) in self.grid_controller.grid.items():
                #         if (level_info.reached == False) and (level >= spread_price):
                #             # level is reached
                #             pass
                #         elif (level_info.reached == True) and (level_info.take_profit_level <= spread_price):
                #             # it's time to execute take profit limit order and clear grid level
                #             pass

            await asyncio.sleep(1)
