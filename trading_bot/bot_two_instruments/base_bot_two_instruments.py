import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from utils.error_checkers import check_grid_direction
from constants import *


from trading_bot.base_trading_bot import BaseTradingBot

from utils import InstrPrices


config = load_config('config.yaml')


class BaseTradingBotTwoInstruments(BaseTradingBot):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        self.check_two_instruments_exits()
        self.instr1_name = config['trading_parameters']['instrument_1']
        self.instr2_name = config['trading_parameters']['instrument_2']
        self.kind1 = config['trading_parameters']['kind_1']
        self.kind2 = config['trading_parameters']['kind_2']
        self.spread_operator = config['trading_parameters']['spread_operator']

        self.two_instr_max_spread_price_deviation = config[
            'trading_parameters']['two_instr_max_spread_price_deviation']

        # self.order1_type = None
        # self.order2_type = None

        # self.initial_instr1_price = None
        # self.initial_instr2_price = None
        # self.initial_spread_price = None

        # self.current_instr1_price = None
        # self.current_instr2_price = None
        # self.current_spread_price = None

        # self.initial_amount1 = None
        # self.initial_amount2 = None
        # self.current_amount1 = None
        # self.current_amount2 = None

        # self.active_spreads = []
        # self.active_positions = []
        # self.take_profit_spreads = []

    async def calculate_portfolio_value(self) -> float:
        instr1_prices = InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr1_name)))
        instr2_prices = InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr2_name)))
        price1 = (instr1_prices.best_bid + instr1_prices.best_ask) / 2
        price2 = (instr2_prices.best_bid + instr2_prices.best_ask) / 2
        currency1 = await self.conn.get_currency_from_instrument(instrument_name=self.instr1_name)
        currency2 = await self.conn.get_currency_from_instrument(instrument_name=self.instr2_name)
        amount1 = await self.conn.get_position(currency=currency1, instrument_name=self.instr1_name)
        amount2 = await self.conn.get_position(currency=currency2, instrument_name=self.instr2_name)
        total_portfolio_value = price1 * amount1 + price2 * amount2
        # print(amount1, amount2)
        # print(price1, price2)
        return total_portfolio_value

    ### Checkers ###

    async def check_total_take_profit(self):
        if self.start_deposit is None:
            raise ValueError('start_deposit is not specified in config.yaml')
        current_portfolio_value = await self.calculate_portfolio_value()
        # print(current_portfolio_value)
        if current_portfolio_value >= self.start_deposit * (1 + self.take_profit_deposit):
            await self.telegram_bot.send_message('Total take profit is reached, bot is stopped')
            await self.conn.cancel_all_orders(instrument_name=self.instr1_name)
            await self.conn.cancel_all_orders(instrument_name=self.instr2_name)
            raise ValueError('Total take profit is reached')

    @staticmethod
    def check_two_instruments_exits():
        if config['trading_parameters']['instrument_1'] in [None, 'None', '-', '']:
            raise ValueError('instrument_1 is not specified')
        if config['trading_parameters']['instrument_2'] in [None, 'None', '-', '']:
            raise ValueError('instrument_2 is not specified')
        if config['trading_parameters']['kind_1'] in [None, 'None', '-', '']:
            raise ValueError('kind_1 is not specified')
        if config['trading_parameters']['kind_2'] in [None, 'None', '-', '']:
            raise ValueError('kind_2 is not specified')
