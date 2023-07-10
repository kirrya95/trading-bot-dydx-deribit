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

        self.active_limit_orders = {}
        self.limit_take_profit_orders = {}  # limit -> take profit
        self.take_profit_limit_orders = {}  # take profit -> limit
        # self.waiting_for_take_profit_orders = {}

    async def check_limit_order_fullfilled(self, active_limit_order) -> bool:
        order_info = await self.conn.get_order(order_id=active_limit_order['order_id'])
        order_state = order_info['order_state']
        order_direction = order_info['direction']
        if order_state == 'filled':
            take_profit_direction = ORDER_SIDE_SELL if order_direction == ORDER_SIDE_BUY else ORDER_SIDE_BUY
            take_profit_order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                   amount=self.size,
                                                                   price=order_info['price'] +
                                                                   self.grid_step,
                                                                   action=take_profit_direction)
            # pop from active limit orders
            self.active_limit_orders.pop(active_limit_order['order_id'])
            # update first dict
            self.limit_take_profit_orders[active_limit_order['order_id']
                                          ] = take_profit_order
            # update second dict
            self.take_profit_limit_orders[take_profit_order['order_id']
                                          ] = active_limit_order
            return True
        else:
            return False

    async def check_take_profit_order_fullfilled(self, take_profit_order) -> bool:
        take_profit_order_info = await self.conn.get_order(order_id=take_profit_order['order_id'])
        take_profit_order_state = take_profit_order_info['order_state']
        if take_profit_order_state == 'filled':
            limit_order = self.take_profit_limit_orders[take_profit_order['order_id']]
            # remove from first dict
            self.take_profit_limit_orders.pop(
                take_profit_order['order_id'])
            # remove from second dict
            self.limit_take_profit_orders.pop(limit_order['order_id'])
            # create limit order
            self.conn.create_limit_order(instrument_name=self.instr_name,
                                         amount=self.size,
                                         price=limit_order['price'],
                                         action=limit_order['direction'])
            self.active_limit_orders[limit_order['order_id']] = limit_order
            return True
        else:
            return False

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

        order_info = await self.conn.get_order(order_id='ETH-4216344391')
        print('order info:', order_info)

        local_grid = await self.calculate_local_grid()

        currency = self.conn.get_currency_from_instrument(
            instrument_name=self.instr_name)
        ndigits_rounding = NDIGITS_ETH_PRICE_ROUNDING if currency == 'ETH' else NDIGITS_BTC_PRICE_ROUNDING

        for grid_level in local_grid:
            grid_level = round(grid_level, ndigits=ndigits_rounding)ƒ

            if self.side == 'long':
                if grid_level >= self.initial_instr_price or self.current_instr_price > grid_level:
                    continue
                self.conn.create_limit_order(instrument_name=self.instr_name,
                                                amount=self.size,
                                                price=grid_level,
                                                action=ORDER_SIDE_BUY)
                self.active_limit_orders[grid_level] = grid_level
            elif self.side == 'short':
                if grid_level <= self.initial_instr_price or self.current_instr_price < grid_level:
                    continue
                self.conn.create_limit_order(instrument_name=self.instr_name,
                                                amount=self.size,
                                                price=grid_level,
                                                action=ORDER_SIDE_SELL)
                self.active_limit_orders[grid_level] = grid_level



        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price()
                self.current_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)

                print('instrument price:', self.current_instr_price)
                print('local grid:', local_grid)
                print('take profit spreads:', self.take_profit_asset_prices)

                for active_limit_order in self.active_limit_orders.keys():
                    await self.check_limit_order_fullfilled(active_limit_order=active_limit_order)

                for waiting_for_take_profit_order in self.waiting_for_take_profit_orders:
                    order_id = waiting_for_take_profit_order['order_id']
                    order_info = await self.conn.get_order(order_id=order_id)
                    order_state = order_info['order_state']
                    if order_state == 'filled':
                        self.waiting_for_take_profit_orders.remove(
                            waiting_for_take_profit_order)

                for order_price in local_grid:
                    order_price = round(
                        order_price, NDIGITS_ETH_PRICE_ROUNDING)
                    if self.side == 'long' and self.current_instr_price <= order_price or True:
                        order = await self.conn.create_limit_order(instrument_name=self.instr_name,
                                                                   amount=self.size,
                                                                   price=order_price,
                                                                   action=ORDER_SIDE_BUY)
                    print(order)
                    # elif self.side == 'short' and self.current_instr_price >= order_price:
                    #     await self.place_limit_order(instrument_name=self.instr_name,
                    #                                  order_side=ORDER_SIDE_SELL,
                    #                                  order_price=order_price,
                    #                                  order_size=self.size)

            await asyncio.sleep(1)
