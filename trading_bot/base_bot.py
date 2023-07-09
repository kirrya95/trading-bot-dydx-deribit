import asyncio
import time
from abc import ABC, abstractmethod

from connectors import AbstractConnector
from telegram_bot import TelegramNotifier

from utils import load_config, to_utc_timestamp
from constants import *


config = load_config('config.yaml')


class BaseTradingBot(ABC):
    def __init__(self,
                 conn: AbstractConnector,
                 telegram_bot: TelegramNotifier):

        self.lock = asyncio.Lock()

        self.conn = conn
        self.telegram_bot = telegram_bot
        self.platform = config['trading_parameters']['platform']
        self.size = config['trading_parameters']['order_size']
        self.grid_step = config['trading_parameters']['grid_step']
        self.take_profit_step = config['trading_parameters']['take_profit_spread_delta']
        self.side = config['trading_parameters']['grid_direction']
        self.start_timestamp = to_utc_timestamp(
            config['trading_parameters']['start_datetime'])
        self.orders_in_market = config['trading_parameters']['orders_in_market']

    async def get_seconds_until_start(self):
        current_timestamp = time.time()
        return max(self.start_timestamp - current_timestamp, 0)

    async def tidy_instrument_amount(self,
                                     instrument_name: str,
                                     amount_in_usdc_to_have: float,
                                     ):

        currency = await self.conn.get_currency_from_instrument(
            instrument_name=instrument_name)
        instrument_amount_usdc = await self.conn.get_position(currency=currency, instrument_name=instrument_name)
        print(f"Current {instrument_name} amount: {instrument_amount_usdc}")

        if instrument_amount_usdc < amount_in_usdc_to_have:
            res = await self.conn.execute_market_order(
                instrument_name=instrument_name,
                amount=amount_in_usdc_to_have - instrument_amount_usdc,
                side=ORDER_SIDE_BUY
            )
            return res
        elif instrument_amount_usdc > amount_in_usdc_to_have:
            res = await self.conn.execute_market_order(
                instrument_name=instrument_name,
                amount=instrument_amount_usdc - amount_in_usdc_to_have,
                side=ORDER_SIDE_SELL
            )
            return res

    async def send_strategy_info(self):
        await asyncio.sleep(2)
        instr1_name = config['trading_parameters']['instrument_1']
        instr2_name = config['trading_parameters']['instrument_2']
        updates_interval = config['trading_parameters']['send_updates_interval']

        if instr2_name != '-':
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
                        # instr1_initial_amount=instr1_initial_amount,
                        # instr2_initial_amount=instr2_initial_amount,
                        instr1_amount=instr1_amount,
                        instr2_amount=instr2_amount,
                        working_time=working_time
                    )
                await asyncio.sleep(updates_interval)
