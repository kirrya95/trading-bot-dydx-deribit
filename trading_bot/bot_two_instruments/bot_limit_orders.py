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
        

    async def create_batch_limit_order(self, instr1_amount, instr2_amount, prices_instr1, prices_instr2, instr1_side, instr2_side) -> dict:

        instr1_price = get_side_price_from_dict_prices(
            instr_prices=prices_instr1, side=instr1_side)
        instr2_price = get_side_price_from_dict_prices(
            instr_prices=prices_instr2, side=instr2_side)

        print('instr 1 price', instr1_price)
        print('instr 2 price', instr2_price)
        print('instr 1 amount', instr1_amount)
        print('instr 2 amount', instr2_amount)

        instr1_limit_order = await self.conn.create_limit_order(instrument_name=self.instr1_name,
                                                                amount=instr1_amount,
                                                                price=instr1_price,
                                                                action=instr1_side)
        instr2_limit_order = await self.conn.create_limit_order(instrument_name=self.instr2_name,
                                                                amount=instr2_amount,
                                                                price=instr2_price,
                                                                action=instr2_side)
        instr1_limit_order_id = instr1_limit_order['order_id']
        instr2_limit_order_id = instr2_limit_order['order_id']

        order1_done = False
        order2_done = False
        while order1_done != True and order2_done != True:
            order1_state = (await self.conn.get_order(order_id=instr1_limit_order_id))['order_state']
            order2_state = (await self.conn.get_order(order_id=instr2_limit_order_id))['order_state']
            if order1_state == 'filled':
                order1_done = True
            if order2_state == 'filled':
                order2_done = True
            if order1_done == True and order2_done == False:
                (current_prices_instr1, current_prices_instr2, current_spread_price) = await self.get_instr_prices_and_spread()
                if abs(current_prices_instr2-instr2_price)/current_prices_instr2 > self.two_instr_max_spread_price_deviation:
                    await self.conn.execute_market_order(
                        instrument_name=self.instr2_name,
                        amount=instr2_amount,
                        side=instr2_side
                    )
                    order2_done = True
            if order1_done == False and order2_done == True:
                (current_prices_instr1, current_prices_instr2, current_spread_price) = await self.get_instr_prices_and_spread()
                if abs(current_prices_instr1-instr1_price)/current_prices_instr1 > self.two_instr_max_spread_price_deviation:
                    await self.conn.execute_market_order(
                        instrument_name=self.instr2_name,
                        amount=instr1_amount,
                        side=instr2_side
                    )
                    order1_done = True



            asyncio.wait(1)

        await self.telegram_bot.send_message(
            f'Created orders on {self.instr1_name} and {self.instr2_name}')

        return instr1_limit_order, instr2_limit_order

    async def get_instr_prices_and_spread(self):
        current_prices_instr1 = await self.conn.get_asset_price(instrument_name=self.instr1_name)
        current_prices_instr2 = await self.conn.get_asset_price(instrument_name=self.instr2_name)

        current_spread_price = await self.get_spread_price_from_two_instr_prices(instr1_prices=current_prices_instr1,
                                                                                 instr2_prices=current_prices_instr2,
                                                                                 grid_direction=self.anti_grid_direction)
        return (current_prices_instr1, current_prices_instr2, current_spread_price)

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
                # current_prices_instr1 = await self.conn.get_asset_price(instrument_name=self.instr1_name)
                # current_prices_instr2 = await self.conn.get_asset_price(instrument_name=self.instr2_name)

                # current_spread_price = await self.get_spread_price_from_two_instr_prices(instr1_prices=current_prices_instr1,
                #                                                                               instr2_prices=current_prices_instr2,
                #                                                                               grid_direction=self.anti_grid_direction)

                (current_prices_instr1, current_prices_instr2, current_spread_price) = await self.get_instr_prices_and_spread()

            print('filtered current grid:', await self.grid_controller.get_filtered_grid())
            print('current spread price:', current_spread_price)

            for grid_level in await self.grid_controller.get_filtered_grid():
                if grid_level >= current_spread_price:
                    instr1_side = get_side_from_direction(
                        direction=self.grid_direction)
                    instr2_side = get_side_from_direction(
                        direction=self.anti_grid_direction)
                    amount1 = await self.get_size_to_trade(instr_name=self.instr1_name, side=instr1_side, kind=self.kind1)
                    amount2 = await self.get_size_to_trade(instr_name=self.instr2_name, side=instr2_side, kind=self.kind2)
                    print('amount1', amount1)
                    print('amount2', amount2)

                    await self.create_batch_limit_order(instr1_amount=amount1,
                                                        instr2_amount=amount2,
                                                        prices_instr1=current_prices_instr1,
                                                        prices_instr2=current_prices_instr2,
                                                        instr1_side=instr1_side,
                                                        instr2_side=instr2_side)
                    await self.grid_controller.update_last_achieved_level(level=grid_level)


if __name__ == '__main__':
    pass
