import asyncio
import time
import typing as tp
from abc import ABC, abstractmethod

from telegram_bot import TelegramNotifier

from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from utils.error_checkers import *
from constants import *


config = load_config('config.yaml')


class BaseTradingBot(ABC):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):

        self.lock = asyncio.Lock()

        self.conn = conn
        self.telegram_bot = telegram_bot
        self.platform = config['trading_parameters']['platform']
        self.size = config['trading_parameters']['order_size']
        self.grid_step = config['trading_parameters']['grid_step']
        self.take_profit_grid_delta = config['trading_parameters']['take_profit_grid_delta']
        self.grid_direction = config['trading_parameters']['grid_direction']
        self.start_timestamp = to_utc_timestamp(
            config['trading_parameters']['start_datetime'])
        self.orders_in_market = config['trading_parameters']['orders_in_market']
        self.max_orders_amount = config['trading_parameters']['max_orders_amount']

        self.start_deposit = config['trading_parameters']['start_deposit']
        self.take_profit_deposit = config['trading_parameters']['take_profit_deposit']
        # self.initial_usdc_deposit_on_wallet = None

        self.anti_grid_direction = GridDirections.GRID_DIRECTION_SHORT if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else GridDirections.GRID_DIRECTION_LONG

        self.limit_order_side = OrderSides.ORDER_SIDE_BUY if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_SELL
        self.take_profit_side = OrderSides.ORDER_SIDE_SELL if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_BUY

    async def get_seconds_until_start(self):
        current_timestamp = time.time()
        return max(self.start_timestamp - current_timestamp, 0)

    # async def check_total_take_profit_reach(self, current_deposit_usdc: float):
    #     # take_profit_deposit = config['trading_parameters']['take_profit_deposit']
    #     if self.side == 'long' and current_deposit_usdc >= self.take_profit_step:
    #         return True
    #     elif self.side == 'short' and current_deposit_usdc <= -self.take_profit_step:
    #         return True
    #     else:
    #         return False

    # async def tidy_instrument_amount(self,
    #                                  instrument_name: str,
    #                                  amount_in_usdc_to_have: float,
    #                                  ):

    #     currency = await self.conn.get_currency_from_instrument(
    #         instrument_name=instrument_name)
    #     instrument_amount_usdc = await self.conn.get_position(currency=currency, instrument_name=instrument_name)
    #     print(f"Current {instrument_name} amount: {instrument_amount_usdc}")

    #     if instrument_amount_usdc < amount_in_usdc_to_have:
    #         res = await self.conn.execute_market_order(
    #             instrument_name=instrument_name,
    #             amount=amount_in_usdc_to_have - instrument_amount_usdc,
    #             side=OrderSides.ORDER_SIDE_BUY
    #         )
    #         return res
    #     elif instrument_amount_usdc > amount_in_usdc_to_have:
    #         res = await self.conn.execute_market_order(
    #             instrument_name=instrument_name,
    #             amount=instrument_amount_usdc - amount_in_usdc_to_have,
    #             side=OrderSides.ORDER_SIDE_SELL
    #         )
    #         return res

    # async def get_asset_amount_usdc(self, instrument_name: str):
    #     currency = await self.conn.get_currency_from_instrument(
    #         instrument_name=instrument_name)
    #     amount = await self.conn.get_position(currency=currency, instrument_name=instrument_name)
    #     return amount

    # @check_side
    # async def get_size_to_trade(self, instr_name, side, kind):

    #     if kind == 'future':
    #         size = config['trading_parameters']['order_size']
    #     elif kind == DeribitAvailableKinds.SPOT:
    #         if instr_name == DeribitSpotMarkets.ETH_BTC:
    #             if side == OrderSides.ORDER_SIDE_BUY:
    #                 price = (await self.conn.get_asset_price(DeribitSpotMarkets.ETH_USDC))['best_ask']
    #                 print(f'Price: {price}')
    #                 size = config['trading_parameters']['order_size'] / price
    #                 return round(size, ndigits=NDIGITS_PRICES_ROUNDING[DeribitSpotMarkets.ETH_USDC])
    #             elif side == OrderSides.ORDER_SIDE_SELL:
    #                 price = (await self.conn.get_asset_price(DeribitSpotMarkets.BTC_USDC))['best_bid']
    #                 print(f'Price: {price}')
    #                 size = config['trading_parameters']['order_size'] / price
    #                 return round(size, ndigits=NDIGITS_PRICES_ROUNDING[DeribitSpotMarkets.BTC_USDC])
    #         else:
    #             size = config['trading_parameters']['order_size'] / \
    #                 self.current_instr_price

    #     else:
    #         raise ValueError('Incorrect kind. Should be either future or spot')

    #    return round(size, ndigits=NDIGITS_PRICES_ROUNDING[instr_name])

    async def send_strategy_info(self):
        instr1_name = config['trading_parameters']['instrument_1']
        instr2_name = config['trading_parameters']['instrument_2']
        instr1_kind = config['trading_parameters']['kind_1']
        instr2_kind = config['trading_parameters']['kind_2']
        updates_interval = config['telegram']['reporting_interval']
        await asyncio.sleep(await self.get_seconds_until_start())
        await asyncio.sleep(updates_interval)

        if instr2_name == '-':
            while True:
                async with self.lock:
                    currency1 = await self.conn.get_currency_from_instrument(instrument_name=instr1_name)
                    _instr1_amount = await self.conn.get_position(currency=currency1, instrument_name=instr1_name)
                    instr1_price = (await self.conn.get_asset_price(instrument_name=instr1_name))[0]
                    instr1_amount = round(_instr1_amount / instr1_price, 8)
                    print(
                        f"Current {instr1_name} amount: {instr1_amount}")
                    working_time = round(time.time() - self.start_timestamp)
                    # usdc_balance = (await self.conn.get_balance(currency="USDC"))['data'][0]['amount']
                    usdc_balance = 0
                    # print(f"USDC balance: {usdc_balance}")
                    current_deposit = (instr1_amount + usdc_balance) - \
                        self.initial_usdc_deposit_on_wallet + self.start_deposit

                    await self.telegram_bot.account_info_one_instrument(
                        current_deposit=current_deposit,
                        kind_name=instr1_kind,
                        instr_name=instr1_name,
                        instr_amount=instr1_amount,
                        working_time=working_time
                    )
                await asyncio.sleep(updates_interval)
        elif instr2_name != '-':
            while True:
                async with self.lock:
                    currency1 = await self.conn.get_currency_from_instrument(instrument_name=instr1_name)
                    currency2 = await self.conn.get_currency_from_instrument(instrument_name=instr2_name)
                    instr1_amount = await self.conn.get_position(currency=currency1, instrument_name=instr1_name)
                    instr2_amount = await self.conn.get_position(currency=currency2, instrument_name=instr2_name)
                    working_time = round(time.time() - self.start_timestamp)
                    current_deposit = instr1_amount + instr2_amount

                    await self.telegram_bot.account_info_two_instruments(
                        current_deposit=current_deposit,
                        instr1_name=instr1_name,
                        instr2_name=instr2_name,
                        kind1=instr1_kind,
                        kind2=instr2_kind,
                        # instr1_initial_amount=instr1_initial_amount,
                        # instr2_initial_amount=instr2_initial_amount,
                        instr1_amount=instr1_amount,
                        instr2_amount=instr2_amount,
                        working_time=working_time
                    )
                await asyncio.sleep(updates_interval)
