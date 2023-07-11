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


config = load_config('config.yaml')


class TradingBotOneInstrumentLimitOrders(BaseTradingBotOneInstrument):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.active_limit_orders = {}
        # self.active_grid_prices = []
        self.limit_take_profit_orders = {}  # limit -> take profit
        self.take_profit_limit_orders = {}  # take profit -> limit
        # self.waiting_for_take_profit_orders = {}

    async def check_limit_order_fullfilled(self, active_limit_order_id) -> bool:
        # print(active_limit_order_id)
        # print('HERE')
        limit_order_info = await self.conn.get_order(order_id=active_limit_order_id)
        order_state = limit_order_info['order_state']
        order_direction = limit_order_info['direction'].upper()
        take_profit_direction = ORDER_SIDE_SELL if order_direction == ORDER_SIDE_BUY else ORDER_SIDE_BUY
        if order_state == 'filled':
            take_profit_price = round(limit_order_info['price'] +
                                      self.take_profit_step if order_direction == ORDER_SIDE_BUY else limit_order_info[
                'price'] - self.take_profit_step, ndigits=self.ndigits_rounding)
            take_profit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                   amount=self.size,
                                                                   price=take_profit_price,
                                                                   action=take_profit_direction)
            # pop from active limit orders
            self.active_limit_orders.pop(active_limit_order_id)
            # add new active limit order (i.e, overall, just updating)
            self.active_limit_orders[limit_order_info['order_id']
                                     ] = limit_order_info
            # update first dict
            self.limit_take_profit_orders[limit_order_info['order_id']
                                          ] = take_profit_order
            # update second dict
            self.take_profit_limit_orders[take_profit_order['order_id']
                                          ] = limit_order_info
            await self.telegram_bot.send_message(
                f'Limit order at the price {limit_order_info["price"]} was filled.'
                f'Take profit order was with the price {take_profit_order["price"]} was created.')
            return True
        else:
            return False

    async def check_take_profit_order_fullfilled(self, take_profit_order_id) -> bool:
        take_profit_order_info = await self.conn.get_order(order_id=take_profit_order_id)
        take_profit_order_state = take_profit_order_info['order_state']
        if take_profit_order_state == 'filled':
            grid_limit_order = self.take_profit_limit_orders[take_profit_order_id]
            # remove from first dict
            self.take_profit_limit_orders.pop(
                take_profit_order_id)
            # remove from second dict
            self.limit_take_profit_orders.pop(grid_limit_order['order_id'])
            # remove from active limit orders
            self.active_limit_orders.pop(grid_limit_order['order_id'])
            # create grid limit order
            new_grid_limit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                      amount=self.size,
                                                                      price=grid_limit_order['price'],
                                                                      action=grid_limit_order['direction'])
            self.active_limit_orders[grid_limit_order['order_id']
                                     ] = new_grid_limit_order
            return True
        else:
            return False

    async def run(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr_name)

        amount_usdc_to_have = 0  # we don't have to have any amount of asset at the start
        # tidy asset amount
        await self.tidy_instrument_amount(instrument_name=self.instr_name, amount_in_usdc_to_have=amount_usdc_to_have)
        self.initial_instr_price = await self.get_instrument_price()
        # self.initial_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)
        # self.initial_usdc_deposit_on_wallet = (await self.conn.get_balance(currency="USDC"))['data'][0]['amount']
        self.initial_usdc_deposit_on_wallet = 0

        # order_info = await self.conn.get_order(order_id='ETH-4216344391')
        # print('order info:', order_info)

        currency = await self.conn.get_currency_from_instrument(
            instrument_name=self.instr_name)
        self.ndigits_rounding = NDIGITS_PRICES_ROUNDING[currency]
        local_grid = await self.calculate_local_grid()

        for grid_level in local_grid:
            grid_level = round(grid_level, ndigits=self.ndigits_rounding)

            if self.side == 'long':
                if grid_level >= self.initial_instr_price:
                    continue
                order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                           amount=self.size,
                                                           price=grid_level,
                                                           action=ORDER_SIDE_BUY)
                self.active_limit_orders[order['order_id']] = order
            elif self.side == 'short':
                if grid_level <= self.initial_instr_price:
                    continue
                order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                           amount=self.size,
                                                           price=grid_level,
                                                           action=ORDER_SIDE_SELL)
                self.active_limit_orders[order['order_id']] = order

        await self.telegram_bot.send_message('Grid orders were created.')

        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price()
                self.current_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)

                print('instrument price:', self.current_instr_price)
                print('local grid:', local_grid)
                print('take profit spreads:', self.take_profit_asset_prices)

                _active_limit_orders = deepcopy(list(
                                                self.active_limit_orders.keys()))
                for active_limit_order_id in _active_limit_orders:
                    if active_limit_order_id in self.limit_take_profit_orders.keys():
                        continue
                    await self.check_limit_order_fullfilled(active_limit_order_id=active_limit_order_id)

                _take_profit_orders = deepcopy(list(
                                               self.take_profit_limit_orders.keys()))
                for take_profit_order_id in _take_profit_orders:
                    await self.check_take_profit_order_fullfilled(take_profit_order_id=take_profit_order_id)

            await asyncio.sleep(1)
