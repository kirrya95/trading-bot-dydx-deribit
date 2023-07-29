import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *


from .base_bot_one_instrument import BaseTradingBotOneInstrument
from .grid_controller_one_intsrument import GridControllerOneInstrument


config = load_config('config.yaml')


class TradingBotOneInstrumentLimitOrders(BaseTradingBotOneInstrument):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr_name]

        self.grid_controller = GridControllerOneInstrument(
            ndigits_rounding=self.ndigits_rounding)

    async def check_limit_order_fullfilled(self, limit_order_id) -> bool:
        limit_order_info = await self.conn.get_order(order_id=limit_order_id)

        if limit_order_info['order_state'] == 'filled':
            take_profit_size = await self.get_size_to_trade(instr_name=self.instr_name,
                                                            side=self.take_profit_side,
                                                            kind=self.kind)
            take_profit_price = limit_order_info['price'] + \
                self.take_profit_step if self.limit_order_side == OrderSides.ORDER_SIDE_BUY else limit_order_info[
                    'price'] - self.take_profit_step
            take_profit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                   amount=take_profit_size,
                                                                   price=take_profit_price,
                                                                   action=self.take_profit_side)
            await self.grid_controller.update_take_profit_order_info(
                order_id=take_profit_order['order_id'], order_info=take_profit_order)

            await self.grid_controller.link_take_profit_order(
                take_profit_order_id=take_profit_order['order_id'], limit_order_id=limit_order_info['order_id'])

            if self.grid_controller.grid_size < self.max_orders_amount:
                await self.grid_controller.change_grid_size(delta=+1)
                new_limit_order_price = self.grid_controller.current_grid[-1]
                new_limit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                     amount=take_profit_size,
                                                                     price=new_limit_order_price,
                                                                     action=self.limit_order_side)
                await self.grid_controller.update_active_order_info(
                    order_id=new_limit_order['order_id'], order_info=new_limit_order)

                await self.telegram_bot.send_message(
                    f'Limit order at the price {limit_order_info["price"]} was filled. \n'
                    f'Take profit order with the price {take_profit_order["price"]} was created. \n'
                    f'New limit order with the price {new_limit_order["price"]} was created.')
            else:
                await self.telegram_bot.send_message(
                    f'Limit order at the price {limit_order_info["price"]} was filled. \n'
                    f'Take profit order with the price {take_profit_order["price"]} was created. \n'
                    f'No new limit order was created because the maximum number of orders was reached.')

            return True
        else:
            return False

    async def check_take_profit_order_fullfilled(self, take_profit_order_id) -> bool:
        take_profit_order_info = await self.conn.get_order(order_id=take_profit_order_id)
        # take_profit_order_state = take_profit_order_info['order_state']
        if take_profit_order_info['order_state'] == 'filled':
            # grid_limit_order = self.take_profit_limit_orders[take_profit_order_id]
            limit_order_id = await self.grid_controller.get_limit_order_id_by_take_profit_order_id(take_profit_order_id=take_profit_order_id)
            limit_order_info = await self.grid_controller.get_active_limit_order_info(order_id=limit_order_id)

            await self.grid_controller.remove_limit_order(order_id=limit_order_id)

            size = await self.get_size_to_trade(side=self.limit_order_side, instr_name=self.instr_name)

            # create grid limit order
            new_limit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                 amount=size,
                                                                 price=limit_order_info['price'],
                                                                 action=limit_order_info['direction'])
            await self.grid_controller.update_active_order_info(
                order_id=new_limit_order['order_id'], order_info=new_limit_order)

            await self.telegram_bot.send_message(
                f'Take profit order at the price {take_profit_order_info["price"]} was filled.'
                f'Limit order with the price {new_limit_order["price"]} was created.')
            return True
        else:
            return False

    async def fill_grid_with_limit_orders(self):
        size = await self.get_size_to_trade(instr_name=self.instr_name,
                                            side=self.limit_order_side,
                                            kind=self.kind)
        for grid_level in self.grid_controller.initial_grid:
            order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                       amount=size,
                                                       price=grid_level,
                                                       action=self.limit_order_side)
            print(order)
            await self.grid_controller.update_active_order_info(
                order_id=order['order_id'], order_info=order)

        await self.telegram_bot.send_message('Grid orders are created.')

    async def run(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr_name, kind=self.kind)
        # take profit side is opposite to limit order side
        self.initial_instr_price = await self.get_instrument_price(side=self.take_profit_side)
        # important for some reasons
        self.current_instr_price = self.initial_instr_price

        print(self.grid_direction)
        await self.grid_controller.initialize_grid(instr_price=self.initial_instr_price,
                                                   grid_size=self.orders_in_market,
                                                   grid_direction=self.grid_direction)

        await self.fill_grid_with_limit_orders()

        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price(side=self.take_profit_side)
                print('current grid:', self.grid_controller.current_grid)

                active_limit_orders_ids = await self.grid_controller.get_active_limit_orders_ids()
                print(active_limit_orders_ids)
                for active_limit_order_id in active_limit_orders_ids:
                    if active_limit_order_id not in await self.grid_controller.get_linked_limit_orders_ids():
                        await self.check_limit_order_fullfilled(limit_order_id=active_limit_order_id)

                take_profit_orders_ids = await self.grid_controller.get_linked_take_profit_orders_ids()
                for take_profit_order_id in take_profit_orders_ids:
                    await self.check_take_profit_order_fullfilled(take_profit_order_id=take_profit_order_id)

            await asyncio.sleep(1)
