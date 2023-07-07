import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config


NDIGITS_ETH_PRICE_ROUNDING = 2
NDIGITS_BTC_PRICE_ROUNDING = 1

# NDIGITS_ETH_AMOUNT_ROUNDING = 3
# NDIGITS_BTC_AMOUNT_ROUNDING = 3

# ------------ Order Side ------------
ORDER_SIDE_BUY = 'BUY'
ORDER_SIDE_SELL = 'SELL'


config = load_config('config.yaml')


class TradingBot:
    def __init__(self,
                 #  number_of_instruments: int,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 #  conn2: tp.Union[dYdXConnection, DeribitConnection],
                 telegram_bot: TelegramNotifier):

        # self.number_of_instruments = number_of_instruments
        self.conn = conn
        self.telegram_bot = telegram_bot

        self.platform = config['trading_parameters']['platform']
        self.size = float(config['trading_parameters']['order_size'])
        self.grid_step = float(config['trading_parameters']['grid_step'])
        self.side = config['trading_parameters']['grid_direction']

        self.last_triggered_price = None

        self.grid_orders = []
        self.take_profit_orders = []

    async def set_initial_instr_prices(self):
        instr1 = config['trading_parameters']['instrument_1']
        instr2 = config['trading_parameters']['instrument_2']

        if self.side == 'long':
            self.initial_instr1_price = (await self.conn.get_asset_price(
                instrument_name=instr1))[1]
            if instr2 != '-':
                self.initial_instr2_price = self.conn.get_asset_price(
                    instrument_name=instr2)[0]
            else:
                self.initial_instr2_price = None
        elif self.side == 'short':
            self.initial_instr1_price = (await self.conn.get_asset_price(
                instrument_name=instr1))[0]
            if instr2 != '-':
                self.initial_instr2_price = self.conn.get_asset_price(
                    instrument_name=instr2)[1]
            else:
                self.initial_instr2_price = None

    async def tidy_instrument_amount(self,
                                     instrument_name: str,
                                     min_amount_usdc_to_have: float,
                                     ):

        # instr_price = (await self.conn.get_asset_price(
        #     instrument_name=instrument_name))[1]

        currency = self.conn.get_currency_from_instrument(
            instrument_name=instrument_name)

        instrument_amount_usdc = await self.conn.get_position(currency=currency, instrument_name=instrument_name)

        if instrument_amount_usdc < min_amount_usdc_to_have:
            # instrument_amount = instrument_amount_usdc / instr_price
            res = await self.conn.execute_market_order(
                instrument_name=instrument_name,
                amount=min_amount_usdc_to_have - instrument_amount_usdc,
                side=ORDER_SIDE_BUY
            )
            return res

    async def get_spread_price(self, instr1_price: float, instr2_price: float) -> float:
        spread_operator = config['trading_parameters']['spread_operator']

        if spread_operator == '/':
            spread_price = instr1_price / instr2_price
        elif spread_operator == '*':
            spread_price = instr1_price * instr2_price
        # elif spread_operator == '+':
        #     spread_price = instr1_price + instr2_price
        # elif spread_operator == '-':
        #     spread_price = instr1_price - instr2_price
        else:
            raise ValueError(f"Invalid spread operator: {spread_operator}")

        return spread_price

    # TODO: implement
    async def get_take_profit_price(self, spread_price: float) -> float:
        self.grid_step
        self.side
        # self.percent

        # return 1 - sum()

    def remove_all_orders(self):
        self.conn.cancel_all_orders()

    # async def create_grid_orders(self, instrument, instrument_price: float):
    #     # spread_price = self.get_spread_price(instr1_price, instr2_price)
    #     # order1_usd_amount = round(
    #     #     self.size / instr1_price, ndigits=NDIGITS_ETH_AMOUNT_ROUNDING)

    #     number_of_orders = config['trading_parameters']['orders_in_market']
    #     if self.side == 'long':
    #         for i in range(1, number_of_orders+1):
    #             grid_price = spread_price - self.grid_step * i
    #             instr_1_price = round(
    #                 grid_price * instr2_price, ndigits=NDIGITS_ETH_PRICE_ROUNDING)
    #             instr_2_price = instr1_price / grid_price
    #             print(instr_1_price)
    #             res = self.conn.create_limit_order(
    #                 instrument_name='ETH-PERPETUAL', amount=order1_usd_amount, price=instr_1_price, action=ORDER_SIDE_BUY)
    #             # print(res)
    #             # break

    async def create_grid_orders_one_instrument(self, instrument_name: str, instrument_price: float):
        number_of_orders = config['trading_parameters']['orders_in_market']

        if self.side == 'long':
            for i in range(1, number_of_orders+1):
                grid_price = instrument_price - self.grid_step * i
                print(grid_price)
                res = await self.conn.create_limit_order(
                    instrument_name=instrument_name, amount=self.size, price=grid_price, action=ORDER_SIDE_BUY)
                self.grid_orders.append(res)
                print(res)
                # break

    async def run_bot_one_instrument(self, instrument_name: str):
        min_amount_usdc_to_have = config['trading_parameters']['start_deposit'] / 2

        print(await self.conn.get_all_orders(currency=instrument_name.split('-')[0], instrument_name=instrument_name))

        # await self.tidy_instrument_amount(instrument_name=instrument_name, min_amount_usdc_to_have=min_amount_usdc_to_have)
        # await self.set_initial_instr_prices()
        # await self.create_grid_orders_one_instrument(instrument_name=instrument_name, instrument_price=self.initial_instr1_price)
        # print(self.initial_instr1_price, self.initial_instr2_price)
        # print(await self.get_spread_price(self.initial_instr1_price,
        #                                   self.initial_instr2_price))
        # await asyncio.sleep(5)

        return
        while True:
            all_orders = await self.conn.get_all_orders(currency=instrument_name.split('-')[0], instrument_name=instrument_name)
            for order in all_orders:
                if order in self.grid_orders and order['order_state'] == 'filled':
                    price_of_executed_order = order['price']
                    take_profit_price = price_of_executed_order + \
                        config['trading_parameters']['take_profit_for_order']
                    take_profit_order_side = ORDER_SIDE_SELL if self.side == 'long' else ORDER_SIDE_BUY
                    take_profit_order_amount = order['max_show']
                    res = await self.conn.create_limit_order(
                        instrument_name=instrument_name,
                        amount=take_profit_order_amount,
                        price=take_profit_price,
                        action=take_profit_order_side)
                    self.take_profit_orders.append(res)
                elif order in self.take_profit_orders:
                    pass
                else:
                    self.conn.cancel_order(order['order_id'])

            # self.create_grid_orders(instr_price, instr_price)
            await asyncio.sleep(5)

        #     break

    async def run_bot_two_instruments(self, instr1_name: str, instr2_name: str):
        min_amount_usdc_to_have = config['trading_parameters']['start_deposit'] / 2

        await self.tidy_instrument_amount(instrument_name=instr1_name, min_amount_usdc_to_have=min_amount_usdc_to_have)
        await self.tidy_instrument_amount(instrument_name=instr2_name, min_amount_usdc_to_have=min_amount_usdc_to_have)

        while True:
            instr1_price = (await self.conn.get_asset_price(
                instrument_name=instr1_name))[1]
            instr2_price = (await self.conn.get_asset_price(
                instrument_name=instr2_name))[1]
            self.create_grid_orders(instr1_price, instr2_price)
            await asyncio.sleep(5)

            # current_price = self.conn.get_asset_price(
            #     instrument_name=instrument_name)
            # await self.create_grid_orders_one_instrument(instrument_name=instrument_name, instrument_price=self.initial_instr1_price)
            break

    async def listen_to_orders(self):
        pass

    # async def run_dydx_bot(self):
    #     # removing all previous orders before the start
    #     self.remove_all_orders()

    #     timedelta = float(
    #         config['trading_parameters']['refresh_interval_ms'] / 1000)

    #     while True:
    #         market_price1 = self.conn1.get_index_price()
    #         market_price2 = self.conn2.get_index_price()

    #         # spread_price = self.get_spread_price(market_price1, market_price2)

    #         self.create_grid_orders(market_price1, market_price2)

    #         time.sleep(timedelta)
    #         break
