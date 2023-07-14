import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from trading_bot.base_trading_bot import BaseTradingBot


config = load_config('config.yaml')


class BaseTradingBotTwoInstruments(BaseTradingBot):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.instr1_name = config['trading_parameters']['instrument_1']
        self.instr2_name = config['trading_parameters']['instrument_2']
        self.kind1 = config['trading_parameters']['kind_1']
        self.kind2 = config['trading_parameters']['kind_2']

        self.order1_type = None
        self.order2_type = None

        self.initial_instr1_price = None
        self.initial_instr2_price = None
        self.initial_spread_price = None

        self.current_instr1_price = None
        self.current_instr2_price = None
        self.current_spread_price = None

        self.initial_amount1 = None
        self.initial_amount2 = None
        self.current_amount1 = None
        self.current_amount2 = None

        self.active_spreads = []
        self.active_positions = []
        self.take_profit_spreads = []

    async def get_spread_price(self, instr1_price: float, instr2_price: float) -> float:
        spread_operator = config['trading_parameters']['spread_operator']

        if spread_operator == '/':
            spread_price = instr1_price / instr2_price
        elif spread_operator == '*':
            spread_price = instr1_price * instr2_price
        elif spread_operator == '+':
            spread_price = instr1_price + instr2_price
        elif spread_operator == '-':
            spread_price = instr1_price - instr2_price
        else:
            raise ValueError(f"Invalid spread operator: {spread_operator}")
        return spread_price

    async def get_instruments_prices(self):
        if self.side != 'long' and self.side != 'short':
            raise ValueError('Incorrect side. Should be either long or short')

        if self.side == 'long':
            instr1_price = (await self.conn.get_asset_price(
                instrument_name=self.instr1_name))[1]
            instr2_price = (await self.conn.get_asset_price(
                instrument_name=self.instr2_name))[0]
        elif self.side == 'short':
            instr1_price = (await self.conn.get_asset_price(
                instrument_name=self.instr1_name))[0]
            instr2_price = (await self.conn.get_asset_price(
                instrument_name=self.instr2_name))[1]

        spread_price = await self.get_spread_price(
            instr1_price=instr1_price,
            instr2_price=instr2_price
        )
        return instr1_price, instr2_price, spread_price

    async def get_amounts(self):
        amount1 = await self.get_asset_amount_usdc(instrument_name=self.instr1_name)
        amount2 = await self.get_asset_amount_usdc(instrument_name=self.instr2_name)
        return amount1, amount2

    async def calculate_local_grid(self):
        if self.initial_spread_price is None:
            raise ValueError('Initial spread price is not set')
        local_grid_lows = [self.initial_spread_price - self.grid_step *
                           i for i in range(1, self.orders_in_market+1)]
        local_grid_highs = [self.initial_spread_price + self.grid_step * i
                            for i in range(1, self.orders_in_market+1)]
        local_grid = local_grid_lows + local_grid_highs
        return local_grid
