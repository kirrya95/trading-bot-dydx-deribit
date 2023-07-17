import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from trading_bot.base_trading_bot import BaseTradingBot

from utils.error_checkers import *


config = load_config('config.yaml')


class BaseTradingBotOneInstrument(BaseTradingBot):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.instr_name = config['trading_parameters']['instrument_1']
        self.kind = config['trading_parameters']['kind_1']

        self.limit_order_side = OrderSides.ORDER_SIDE_BUY if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_SELL
        self.take_profit_side = OrderSides.ORDER_SIDE_SELL if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_BUY

        self.initial_instr_price = None
        self.current_instr_price = None
        self.initial_amount = None
        self.current_amount = None

        self.initial_usdc_balance = None
        self.current_usdc_balance = None

    async def get_instrument_price(self, side: tp.Union[OrderSides.ORDER_SIDE_BUY, OrderSides.ORDER_SIDE_SELL]) -> float:
        if side not in [OrderSides.ORDER_SIDE_BUY, OrderSides.ORDER_SIDE_SELL]:
            raise ValueError(
                f'Incorrect side. Should be either {OrderSides.ORDER_SIDE_BUY} or {OrderSides.ORDER_SIDE_SELL}')

        print(await self.conn.get_asset_price(instrument_name=self.instr_name))
        # print('HERE')

        if side == OrderSides.ORDER_SIDE_BUY:
            instr_price = (await self.conn.get_asset_price(
                instrument_name=self.instr_name))['best_ask']
        elif side == OrderSides.ORDER_SIDE_SELL:
            instr_price = (await self.conn.get_asset_price(
                instrument_name=self.instr_name))['best_bid']

        return instr_price

    @check_side
    async def get_size_to_trade(self, side):

        if self.kind == 'future':
            size = config['trading_parameters']['order_size']
        elif self.kind == DeribitAvailableKinds.SPOT:
            if self.instr_name == DeribitSpotMarkets.ETH_BTC:
                if side == OrderSides.ORDER_SIDE_BUY:
                    price = (await self.conn.get_asset_price(DeribitSpotMarkets.ETH_USDC))['best_ask']
                    print(f'Price: {price}')
                    size = config['trading_parameters']['order_size'] / price
                    return round(size, ndigits=NDIGITS_PRICES_ROUNDING[DeribitSpotMarkets.ETH_USDC])
                elif side == OrderSides.ORDER_SIDE_SELL:
                    price = (await self.conn.get_asset_price(DeribitSpotMarkets.BTC_USDC))['best_bid']
                    print(f'Price: {price}')
                    size = config['trading_parameters']['order_size'] / price
                    return round(size, ndigits=NDIGITS_PRICES_ROUNDING[DeribitSpotMarkets.BTC_USDC])
            else:
                size = config['trading_parameters']['order_size'] / \
                    self.current_instr_price

        else:
            raise ValueError('Incorrect kind. Should be either future or spot')

        return round(size, ndigits=NDIGITS_PRICES_ROUNDING[self.instr_name])
