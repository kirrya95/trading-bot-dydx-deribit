import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from trading_bot.bot_two_instruments import BaseTradingBotTwoInstruments


config = load_config('config.yaml')


class TradingBotTwoInstrumentsMarketOrders(BaseTradingBotTwoInstruments):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

    #     self.instr1_name = config['trading_parameters']['instrument_1']
    #     self.instr2_name = config['trading_parameters']['instrument_2']

    #     self.order1_type = 'market'
    #     self.order2_type = 'market'

    #     self.initial_instr1_price = None
    #     self.initial_instr2_price = None
    #     self.initial_spread_price = None

    #     self.current_instr1_price = None
    #     self.current_instr2_price = None
    #     self.current_spread_price = None

    #     self.initial_amount1 = None
    #     self.initial_amount2 = None
    #     self.current_amount1 = None
    #     self.current_amount2 = None

    #     self.active_spreads = []
    #     self.active_positions = []
    #     self.take_profit_spreads = []

    # async def get_spread_price(self, instr1_price: float, instr2_price: float) -> float:
    #     spread_operator = config['trading_parameters']['spread_operator']

    #     if spread_operator == '/':
    #         spread_price = instr1_price / instr2_price
    #     elif spread_operator == '*':
    #         spread_price = instr1_price * instr2_price
    #     # elif spread_operator == '+':
    #     #     spread_price = instr1_price + instr2_price
    #     # elif spread_operator == '-':
    #     #     spread_price = instr1_price - instr2_price
    #     else:
    #         raise ValueError(f"Invalid spread operator: {spread_operator}")
    #     return spread_price

    # async def get_instruments_prices(self):
    #     if self.side != 'long' and self.side != 'short':
    #         raise ValueError('Incorrect side. Should be either long or short')

    #     if self.side == 'long':
    #         instr1_price = (await self.conn.get_asset_price(
    #             instrument_name=self.instr1_name))[1]
    #         instr2_price = (await self.conn.get_asset_price(
    #             instrument_name=self.instr2_name))[0]
    #     elif self.side == 'short':
    #         instr1_price = (await self.conn.get_asset_price(
    #             instrument_name=self.instr1_name))[0]
    #         instr2_price = (await self.conn.get_asset_price(
    #             instrument_name=self.instr2_name))[1]

    #     spread_price = await self.get_spread_price(
    #         instr1_price=instr1_price,
    #         instr2_price=instr2_price
    #     )
    #     return instr1_price, instr2_price, spread_price

    # async def get_amounts(self):
    #     # currency1 = await self.conn.get_currency_from_instrument(
    #     #     instrument_name=self.instr1_name)
    #     # amount1 = await self.conn.get_position(currency=currency1, instrument_name=self.instr1_name)

    #     # currency2 = await self.conn.get_currency_from_instrument(
    #     #     instrument_name=self.instr2_name)
    #     # amount2 = await self.conn.get_position(currency=currency2, instrument_name=self.instr2_name)
    #     amount1 = self.get_asset_amount_usdc(instrument_name=self.instr1_name)
    #     amount2 = self.get_asset_amount_usdc(instrument_name=self.instr2_name)
    #     return amount1, amount2

    # async def calculate_local_grid(self):
    #     if self.initial_spread_price is None:
    #         raise ValueError('Initial spread price is not set')
    #     local_grid_lows = [self.initial_spread_price - self.grid_step *
    #                        i for i in range(1, self.orders_in_market+1)]
    #     local_grid_highs = [self.initial_spread_price + self.grid_step * i
    #                         for i in range(1, self.orders_in_market+1)]
    #     local_grid = local_grid_lows + local_grid_highs
    #     return local_grid

    async def check_for_grid_level_take_profit(self, tp_spread):
        if self.side == 'long' and self.current_spread_price >= tp_spread:
            instr1_order = await self.conn.execute_market_order(instrument_name=self.instr1_name, amount=self.size, side=ORDER_SIDE_SELL)
            instr2_order = await self.conn.execute_market_order(instrument_name=self.instr2_name, amount=self.size, side=ORDER_SIDE_BUY)
            self.take_profit_spreads.remove(tp_spread)
        elif self.side == 'short' and self.current_spread_price <= tp_spread:
            instr1_order = await self.conn.execute_market_order(instrument_name=self.instr1_name, amount=self.size, side=ORDER_SIDE_BUY)
            instr2_order = await self.conn.execute_market_order(instrument_name=self.instr2_name, amount=self.size, side=ORDER_SIDE_SELL)
            self.take_profit_spreads.remove(tp_spread)
        else:
            return

        await self.telegram_bot.notify_take_profit_two_instruments(take_profit_level=tp_spread,
                                                                   spread_price=self.current_spread_price,
                                                                   order1=self.instr1_name,  # TODO: change to orders
                                                                   order2=self.instr2_name,
                                                                   order1_type=self.order1_type,
                                                                   order2_type=self.order2_type)

    async def check_for_grid_level(self, grid_level):
        if grid_level in self.active_spreads:
            return
        # self.conn.execute_market_order(instrument_name1=self.instr1_name, amount=self.size, side=ORDER_SIDE_BUY)
        if self.side == 'long':
            if grid_level >= self.initial_spread_price or self.current_spread_price > grid_level:
                return
            instr1_order = await self.conn.execute_market_order(instrument_name=self.instr1_name, amount=self.size, side=ORDER_SIDE_BUY)
            instr2_order = await self.conn.execute_market_order(instrument_name=self.instr2_name, amount=self.size, side=ORDER_SIDE_SELL)
            self.active_spreads.append(grid_level)
            self.take_profit_spreads.append(grid_level + self.take_profit_step)
        elif self.side == 'short':
            if grid_level <= self.initial_spread_price or self.current_spread_price < grid_level:
                return
            instr1_order = await self.conn.execute_market_order(instrument_name=self.instr1_name, amount=self.size, side=ORDER_SIDE_SELL)
            instr2_order = await self.conn.execute_market_order(instrument_name=self.instr2_name, amount=self.size, side=ORDER_SIDE_BUY)
            self.active_spreads.append(grid_level)
            self.take_profit_spreads.append(grid_level + self.take_profit_step)
        else:
            raise ValueError('Incorrect side. Should be either long or short')

        await self.telegram_bot.notify_grid_level_two_instruments(grid_level=grid_level,
                                                                  spread_price=self.current_spread_price,
                                                                  order1=self.instr1_name,  # TODO: change to orders
                                                                  order2=self.instr2_name,
                                                                  order1_type=self.order1_type,
                                                                  order2_type=self.order2_type)

    async def run(self):
        amount_usdc_to_have = config['trading_parameters']['start_deposit'] / 2
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.tidy_instrument_amount(instrument_name=self.instr1_name, amount_in_usdc_to_have=amount_usdc_to_have)
        await self.tidy_instrument_amount(instrument_name=self.instr2_name, amount_in_usdc_to_have=amount_usdc_to_have)
        self.initial_instr1_price, self.initial_instr2_price, self.initial_spread_price = await self.get_instruments_prices()
        self.initial_amount1, self.initial_amount2 = await self.get_amounts()

        while True:
            async with self.lock:
                self.current_instr1_price, self.current_instr2_price, self.current_spread_price = await self.get_instruments_prices()
                self.current_amount1, self.current_amount2 = await self.get_amounts()

                local_grid = await self.calculate_local_grid()
                print('spread price:', self.current_spread_price)
                print('local grid:', local_grid)
                print('take profit spreads:', self.take_profit_spreads)
                for tp_spread in self.take_profit_spreads:
                    await self.check_for_grid_level_take_profit(tp_spread=tp_spread)

                for grid_level in local_grid:
                    await self.check_for_grid_level(grid_level=grid_level)

            await asyncio.sleep(1)