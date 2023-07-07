import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp


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
        self.take_profit_spread_delta = float(
            config['trading_parameters']['take_profit_spread_delta'])
        self.side = config['trading_parameters']['grid_direction']
        self.start_timestamp = to_utc_timestamp(
            config['trading_parameters']['start_datetime'])

        self.number_of_instruments = 1 if config['trading_parameters']['instrument_2'] == '-' else 2

        self.initial_instr1_price = None
        self.initial_instr2_price = None
        self.initial_spread_price = None

        self.current_instr1_price = None
        self.current_instr2_price = None

        # self.grid_orders = []

        self.active_spreads = []
        self.active_positions = []
        self.take_profit_spreads = []

    async def set_initial_instr_prices(self):
        instr1 = config['trading_parameters']['instrument_1']
        instr2 = config['trading_parameters']['instrument_2']

        if self.side == 'long':
            self.initial_instr1_price = (await self.conn.get_asset_price(
                instrument_name=instr1))[1]
            if instr2 != '-':
                self.initial_instr2_price = (await self.conn.get_asset_price(
                    instrument_name=instr2))[0]
            else:
                self.initial_instr2_price = None
        elif self.side == 'short':
            self.initial_instr1_price = (await self.conn.get_asset_price(
                instrument_name=instr1))[0]
            if instr2 != '-':
                self.initial_instr2_price = (await self.conn.get_asset_price(
                    instrument_name=instr2))[1]
            else:
                self.initial_instr2_price = None

        if instr2 != '-':
            self.initial_spread_price = await self.get_spread_price(
                instr1_price=self.initial_instr1_price,
                instr2_price=self.initial_instr2_price
            )

    async def tidy_instrument_amount(self,
                                     instrument_name: str,
                                     min_amount_usdc_to_have: float,
                                     ):

        # instr_price = (await self.conn.get_asset_price(
        #     instrument_name=instrument_name))[1]

        currency = await self.conn.get_currency_from_instrument(
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

    # def remove_all_orders(self):
    #     self.conn.cancel_all_orders()

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
        current_timestamp = time.time()
        # ensuring that bot starts working at the right time
        if (current_timestamp - self.start_timestamp) < 0:
            await asyncio.sleep(self.start_timestamp - current_timestamp)

        await self.tidy_instrument_amount(instrument_name=instr1_name, min_amount_usdc_to_have=min_amount_usdc_to_have)
        await self.tidy_instrument_amount(instrument_name=instr2_name, min_amount_usdc_to_have=min_amount_usdc_to_have)
        await self.set_initial_instr_prices()

        while True:
            if self.side == 'long':
                # if side is long, then we buy instr1 and sell instr2
                self.current_instr1_price = (await self.conn.get_asset_price(
                    instrument_name=instr1_name))[1]
                self.current_instr2_price = (await self.conn.get_asset_price(
                    instrument_name=instr2_name))[0]
            elif self.side == 'short':
                # if side is short, then we sell instr1 and buy instr2
                self.current_instr1_price = (await self.conn.get_asset_price(
                    instrument_name=instr1_name))[0]
                self.current_instr2_price = (await self.conn.get_asset_price(
                    instrument_name=instr2_name))[1]
            else:
                raise ValueError('Side is neither long nor short')

            # calculating spread price
            spread_price = await self.get_spread_price(self.current_instr1_price, self.current_instr2_price)

            local_grid_lows = [self.initial_spread_price - self.grid_step *
                               i for i in range(1, config['trading_parameters']['orders_in_market']+1)]
            local_grid_highs = [self.initial_spread_price + self.grid_step * i
                                for i in range(1, config['trading_parameters']['orders_in_market']+1)]
            local_grid = local_grid_lows + local_grid_highs

            print('spread price:', spread_price)
            print('local grid:', local_grid)

            print('take profit spreads:', self.take_profit_spreads)

            if self.side == 'long':
                for tp_spread in self.take_profit_spreads:
                    if spread_price >= tp_spread:
                        await self.telegram_bot.send_message(
                            f"Reached take profit level \n" +
                            f"Current spread price: {spread_price} \n" +
                            f"Executing take profit (market) orders...")
                        instr1_order = await self.conn.execute_market_order(instrument_name=instr1_name, amount=self.size, side=ORDER_SIDE_SELL)
                        await self.telegram_bot.send_message(
                            "Executed first market order: {}".format(instr1_name))
                        instr2_order = await self.conn.execute_market_order(instrument_name=instr2_name, amount=self.size, side=ORDER_SIDE_BUY)
                        await self.telegram_bot.send_message(
                            "Executed 2nd market order: {}".format(instr2_name))
                        self.take_profit_spreads.remove(tp_spread)

                for grid_spread in local_grid:
                    if grid_spread >= self.initial_spread_price:
                        continue
                    if spread_price > grid_spread:
                        continue
                    if grid_spread in self.active_spreads:
                        continue
                    # await self.telegram_bot.send_message(
                    #     f"Reached grid level \n"
                    #     f"Current spread price: {spread_price} \n"
                    #     f"Executing 2 market orders...")
                    instr1_order = await self.conn.execute_market_order(instrument_name=instr1_name, amount=self.size, side=ORDER_SIDE_BUY)
                    # await self.telegram_bot.send_message(
                    #     "Executed 1st market order: {}".format(instr1_name))
                    instr2_order = await self.conn.execute_market_order(instrument_name=instr2_name, amount=self.size, side=ORDER_SIDE_SELL)
                    # await self.telegram_bot.send_message(
                    #     "Executed 2nd market order: {}".format(instr2_name))
                    await self.telegram_bot.notify_new_orders_two_instruments(spread_price=spread_price,
                                                                              order1=instr1_name,
                                                                              order2=instr2_name,
                                                                              order1_type='market',
                                                                              order2_type='market',)
                    self.active_spreads.append(grid_spread)
                    self.take_profit_spreads.append(
                        grid_spread + self.take_profit_spread_delta)

            elif self.side == 'short':
                pass

            await asyncio.sleep(1)

            # current_price = self.conn.get_asset_price(
            #     instrument_name=instrument_name)
            # await self.create_grid_orders_one_instrument(instrument_name=instrument_name, instrument_price=self.initial_instr1_price)
            # break

    async def send_strategy_info(self):
        await asyncio.sleep(5)

        updates_interval = config['trading_parameters']['send_updates_interval']

        if self.number_of_instruments == 2:

            instr1_name = config['trading_parameters']['instrument_1']
            instr2_name = config['trading_parameters']['instrument_2']
            instr1_initial_amount = 1.5
            instr2_initial_amount = 1.7

            while True:
                instr1_amount = 1.6
                instr2_amount = 1.8
                working_time = round(time.time() - self.start_timestamp)
                current_deposit = self.current_instr1_price * \
                    instr1_amount + self.current_instr2_price * instr2_amount

                await self.telegram_bot.account_info_two_instruments(
                    current_deposit=current_deposit,
                    instr1_name=instr1_name,
                    instr2_name=instr2_name,
                    instr1_initial_amount=instr1_initial_amount,
                    instr2_initial_amount=instr2_initial_amount,
                    instr1_amount=instr1_amount,
                    instr2_amount=instr2_amount,
                    working_time=working_time
                )
                print('hi')
                await asyncio.sleep(updates_interval)

    # async def listen_to_orders(self):
    #     pass

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
