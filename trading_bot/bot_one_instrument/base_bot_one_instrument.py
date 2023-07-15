import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from trading_bot.base_trading_bot import BaseTradingBot


config = load_config('config.yaml')


class BaseTradingBotOneInstrument(BaseTradingBot):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.instr_name = config['trading_parameters']['instrument_1']
        self.kind = config['trading_parameters']['kind_1']

        self.initial_instr_price = None
        self.current_instr_price = None
        self.initial_amount = None
        self.current_amount = None

        self.initial_usdc_balance = None
        self.current_usdc_balance = None

        # self.active_asset_prices = []
        self.active_positions = []
        self.take_profit_asset_prices = []

    async def get_instrument_price(self):
        if self.side != 'long' and self.side != 'short':
            raise ValueError('Incorrect side. Should be either long or short')

        print(await self.conn.get_asset_price(instrument_name=self.instr_name))
        print('HERE')

        if self.side == 'long':
            instr_price = (await self.conn.get_asset_price(
                instrument_name=self.instr_name))[1]
        elif self.side == 'short':
            instr_price = (await self.conn.get_asset_price(
                instrument_name=self.instr_name))[0]

        return instr_price

    async def calculate_local_grid(self):
        if self.initial_instr_price is None:
            raise ValueError('Initial instrument price is not set')
        local_grid_lows = [self.initial_instr_price - self.grid_step *
                           i for i in range(1, self.orders_in_market+1)]
        local_grid_highs = [self.initial_instr_price + self.grid_step * i
                            for i in range(1, self.orders_in_market+1)]
        local_grid = local_grid_lows + local_grid_highs

        return local_grid

    async def get_size_to_trade(self, side=None):
        if self.kind == 'future':
            size = self.size
        elif self.kind == 'spot':
            if self.instr_name == ETH_BTC:
                if side != 'long' and side != 'short':
                    raise ValueError(
                        'Incorrect side. Should be either long or short')
                if side == 'long':
                    price = (await self.conn.get_asset_price('ETH_USDC'))[0]
                    print(f'Price: {price}')
                    size = self.size / price
                elif side == 'short':
                    price = (await self.conn.get_asset_price('BTC_USDC'))[0]
                    print(f'Price: {price}')
                    size = self.size / price
            else:
                size = self.size / self.current_instr_price

        else:
            raise ValueError('Incorrect kind. Should be either future or spot')

        return round(size, ndigits=NDIGITS_PRICES_ROUNDING[self.instr_name])
