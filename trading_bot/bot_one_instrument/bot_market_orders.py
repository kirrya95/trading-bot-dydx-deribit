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


class TradingBotOneInstrumentMarketOrders(BaseTradingBotOneInstrument):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)
        self.order_type = 'market'
        self.active_asset_prices = []

    async def check_for_grid_level_take_profit(self, tp_price: float):
        if self.side == 'long' and self.current_instr_price >= tp_price:
            instr_order = await self.conn.execute_market_order(instrument_name=self.instr_name, amount=self.size, side=ORDER_SIDE_SELL)
            self.take_profit_asset_prices.remove(tp_price)
        elif self.side == 'short' and self.current_instr_price <= tp_price:
            instr_order = await self.conn.execute_market_order(instrument_name=self.instr_name, amount=self.size, side=ORDER_SIDE_BUY)
            self.take_profit_asset_prices.remove(tp_price)
        else:
            return

        await self.telegram_bot.notify_take_profit_one_instrument(take_profit_level=tp_price,
                                                                  instr_price=self.current_instr_price,
                                                                  order=self.instr_name,  # TODO: change to orders
                                                                  order_type=self.order_type)

    async def check_for_grid_level(self, grid_level: float):
        if self.side == 'long':
            if grid_level >= self.initial_instr_price or self.current_instr_price > grid_level:
                return
            instr_order = await self.conn.execute_market_order(instrument_name=self.instr_name, amount=self.size, side=ORDER_SIDE_SELL)
            self.active_asset_prices.append(grid_level)
            self.take_profit_asset_prices.append(
                grid_level + self.take_profit_step)
        elif self.side == 'short':
            if grid_level <= self.initial_instr_price or self.current_instr_price < grid_level:
                return
            instr_order = await self.conn.execute_market_order(instrument_name=self.instr_name, amount=self.size, side=ORDER_SIDE_BUY)
            self.active_asset_prices.append(grid_level)
            self.take_profit_asset_prices.append(
                grid_level + self.take_profit_step)
        else:
            return

        await self.telegram_bot.notify_grid_level_one_instrument(grid_level=grid_level,
                                                                 instr_price=self.current_instr_price,
                                                                 order=self.instr_name,  # TODO: change to orders
                                                                 order_type=self.order_type)

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
        self.initial_usdc_deposit_on_wallet = (await self.conn.get_balance(currency="USDC"))['data'][0]['amount']

        while True:
            async with self.lock:
                self.current_instr_price = await self.get_instrument_price()
                self.current_amount = await self.get_asset_amount_usdc(instrument_name=self.instr_name)

                local_grid = await self.calculate_local_grid()
                print('instrument price:', self.current_instr_price)
                print('local grid:', local_grid)
                print('take profit spreads:', self.take_profit_asset_prices)
                for tp_price in self.take_profit_asset_prices:
                    await self.check_for_grid_level_take_profit(tp_price=tp_price)

                for grid_level in local_grid:
                    await self.check_for_grid_level(grid_level=grid_level)

            await asyncio.sleep(1)
