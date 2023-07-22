import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp, get_direction_from_side, get_side_from_direction
from utils.error_checkers import check_grid_direction
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
        grid_ndigits_rounding = 4

        self.grid_controller = GridControllerTwoInstruments(
            ndigits_rounding=grid_ndigits_rounding)

    async def check_limit_orders_are_fullfilled(self, limit_orders_hash) -> bool:
        pass

    async def check_take_profit_orders_are_fullfilled(self, take_profit_orders_hash) -> bool:
        pass

    @check_grid_direction
    async def create_batch_limit_order(self, instr1_amount, instr2_amount, instr1_price, instr2_price, direction) -> dict:

        if direction == GridDirections.GRID_DIRECTION_LONG:
            instr1_side = OrderSides.ORDER_SIDE_BUY
            instr2_side = OrderSides.ORDER_SIDE_SELL
        elif direction == GridDirections.GRID_DIRECTION_SHORT:
            instr1_side = OrderSides.ORDER_SIDE_SELL
            instr2_side = OrderSides.ORDER_SIDE_BUY

        instr1_limit_order = await self.conn.create_limit_order(instrument_name=self.instr1_name,
                                                                amount=instr1_amount,
                                                                price=instr1_price,
                                                                action=instr1_side)
        instr2_limit_order = await self.conn.create_limit_order(instrument_name=self.instr2_name,
                                                                amount=instr2_amount,
                                                                price=instr2_price,
                                                                action=instr2_side)

        await self.telegram_bot.send_message(
            f'Created orders on {self.instr1_name} and {self.instr2_name}')

    async def run(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr1_name, kind=self.kind1)
        await self.conn.cancel_all_orders(instrument_name=self.instr2_name, kind=self.kind2)

        initial_prices_instr1 = await self.conn.get_asset_price(instrument_name=self.instr1_name)
        initial_prices_instr2 = await self.conn.get_asset_price(instrument_name=self.instr2_name)

        print(self.grid_direction)
        self.initial_spread_price = await self.get_spread_price_from_two_instr_prices(instr1_prices=initial_prices_instr1,
                                                                                      instr2_prices=initial_prices_instr2,
                                                                                      grid_direction=self.grid_direction)
        print('hi')

        await self.grid_controller.initialize_grid(instr_price=self.initial_spread_price,
                                                   grid_size=self.orders_in_market,
                                                   grid_direction=self.grid_direction)

        while True:
            async with self.lock:
                current_prices_instr1 = await self.conn.get_asset_price(instrument_name=self.instr1_name)
                current_prices_instr2 = await self.conn.get_asset_price(instrument_name=self.instr2_name)

                self.current_spread_price = await self.get_spread_price_from_two_instr_prices(instr1_prices=current_prices_instr1,
                                                                                              instr2_prices=current_prices_instr2,
                                                                                              grid_direction=self.anti_grid_direction)

            print('current grid:', self.grid_controller.current_grid)

            for grid_level in await self.grid_controller.get_filtered_grid():
                if grid_level >= self.current_spread_price:
                    side1 = get_side_from_direction(
                        direction=self.grid_direction)
                    side2 = get_side_from_direction(
                        direction=self.anti_grid_direction)
                    amount1 = await self.get_size_to_trade(side=side1, instr_name=self.instr1_name)
                    amount2 = await self.get_size_to_trade(side=side2, instr_name=self.instr2_name)

                    # await self.conn.cancel_all_orders(instrument_name=self.instr1_name, kind=self.kind1)
                    # await self.conn.cancel_all_orders(instrument_name=self.instr2_name, kind=self.kind2)
                    # await self.create_limit_order(instr_name=self.instr1_name,)

                    await self.create_batch_limit_order(instr1_amount=amount1,
                                                        instr2_amount=amount2,
                                                        instr1_price=grid_level,
                                                        instr2_price=grid_level,
                                                        direction=self.grid_direction)
                    await self.grid_controller.update_last_achieved_level(grid_level)


if __name__ == '__main__':
    pass
