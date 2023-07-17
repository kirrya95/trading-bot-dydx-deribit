import typing as tp
import time
import asyncio
from copy import deepcopy

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

# from trading_bot.base_bot import BaseTradingBot

from trading_bot.bot_one_instrument import BaseTradingBotOneInstrument

from .grid_controller import GridController


config = load_config('config.yaml')


class TradingBotOneInstrumentLimitOrders(BaseTradingBotOneInstrument):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr_name]

        self.grid_controller = GridController(
            ndigits_rounding=self.ndigits_rounding)

    async def check_limit_order_fullfilled(self, limit_order_id) -> bool:
        limit_order_info = await self.conn.get_order(order_id=limit_order_id)

        if limit_order_info['order_state'] == 'filled':
            take_profit_size = await self.get_size_to_trade(side=self.take_profit_side)
            take_profit_price = limit_order_info['price'] + \
                self.take_profit_step if self.limit_order_side == ORDER_SIDE_BUY else limit_order_info[
                    'price'] - self.take_profit_step
            take_profit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                   amount=take_profit_size,
                                                                   price=take_profit_price,
                                                                   action=self.take_profit_side)
            await self.grid_controller.update_active_order_info(
                order_id=limit_order_id, order_info=limit_order_info)

            await self.grid_controller.link_take_profit_order(
                take_profit_orde_id=take_profit_order['order_id'], limit_order_id=limit_order_info['order_id'])

            await self.telegram_bot.send_message(
                f'Limit order at the price {limit_order_info["price"]} was filled.'
                f'Take profit order with the price {take_profit_order["price"]} was created.')
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
            await self.grid_controller.remove_take_profit_order(order_id=take_profit_order_id)

            # # remove from first dict
            # self.take_profit_limit_orders.pop(
            #     take_profit_order_id)
            # # remove from second dict
            # self.limit_take_profit_orders.pop(grid_limit_order['order_id'])
            # # remove from active limit orders
            # self.active_limit_orders.pop(grid_limit_order['order_id'])

            size = await self.get_size_to_trade(side=self.limit_order_side)

            # create grid limit order
            new_limit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                 amount=size,
                                                                 price=limit_order_info['price'],
                                                                 action=limit_order_info['direction'])
            self.grid_controller.update_active_order_info(
                order_id=new_limit_order['order_id'], order_info=new_limit_order)

            await self.telegram_bot.send_message(
                f'Take profit order at the price {take_profit_order_info["price"]} was filled.'
                f'Limit order with the price {new_limit_order["price"]} was created.')
            return True
        else:
            return False

    async def fill_grid_with_limit_orders(self):
        size = await self.get_size_to_trade(side=self.limit_order_side)
        for grid_level in self.grid_controller.current_grid:
            order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                       amount=size,
                                                       price=grid_level,
                                                       action=self.limit_order_side)
            self.grid_controller.update_active_order_info(
                order_id=order['order_id'], order_info=order)

        await self.telegram_bot.send_message('Grid orders were created.')

    async def run(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr_name, kind=self.kind)
        self.initial_instr_price = await self.get_instrument_price()
        # important for some reasons
        self.current_instr_price = self.initial_instr_price

        await self.grid_controller.initialize_grid(instr_price=self.initial_instr_price,
                                                   grid_size=self.orders_in_market,
                                                   grid_direction=self.grid_direction)

        await self.fill_grid_with_limit_orders()

        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price()
                print('instrument price:', self.current_instr_price)
                print('current grid:', self.grid_controller.current_grid)

                active_limit_orders_ids = await self.grid_controller.get_active_limit_orders_ids()
                for active_limit_order_id in active_limit_orders_ids:
                    if active_limit_order_id not in await self.grid_controller.get_linked_limit_orders_ids():
                        await self.check_limit_order_fullfilled(active_limit_order_id=active_limit_order_id)

                take_profit_orders_ids = await self.grid_controller.get_linked_take_profit_orders_ids()
                for take_profit_order_id in take_profit_orders_ids:
                    await self.check_take_profit_order_fullfilled(take_profit_order_id=take_profit_order_id)

            await asyncio.sleep(1)
