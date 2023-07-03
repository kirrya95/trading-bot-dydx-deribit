import time


from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx import dYdXConnection
from telegram_bot import TelegramNotifier


NDIGITS_ETH_PRICE_ROUNDING = 1
NDIGITS_BTC_PRICE_ROUNDING = 0
NDIGITS_ETH_AMOUNT_ROUNDING = 3
NDIGITS_BTC_AMOUNT_ROUNDING = 3


class TradingBot:
    def __init__(self,
                 dydx_conn1: dYdXConnection,
                 dydx_conn2: dYdXConnection,
                 telegram_bot: TelegramNotifier,
                 config: dict):
        self.config = config
        self.dydx_conn1 = dydx_conn1
        self.dydx_conn2 = dydx_conn2
        self.telegram_bot = telegram_bot

        self.size = float(config['trading_parameters']['order_size'])
        self.grid_step = float(config['trading_parameters']['grid_step'])
        self.side = config['trading_parameters']['grid_direction']

        self.initial_market_price1 = self.dydx_conn1.get_index_price()
        self.initial_market_price2 = self.dydx_conn2.get_index_price()
        self.initial_spread_price = self.get_spread_price(
            self.initial_market_price1, self.initial_market_price2)

        self.last_triggered_price = None

        # self.grid_orders = []

    def get_spread_price(self, market_price1: float, market_price2: float) -> float:
        spread_operator = self.config['trading_parameters']['spread_operator']

        if spread_operator == '/':
            spread_price = market_price1 / market_price2
        elif spread_operator == '*':
            spread_price = market_price1 * market_price2
        # elif spread_operator == '+':
        #     spread_price = market_price1 + market_price2
        # elif spread_operator == '-':
        #     spread_price = market_price1 - market_price2
        else:
            raise ValueError(f"Invalid spread operator: {spread_operator}")

        return spread_price

    # TODO: implement
    def get_take_profit_price(self, spread_price: float) -> float:
        self.grid_step
        self.side
        # self.percent

        # return 1 - sum()

    def remove_all_orders(self):
        self.dydx_conn1.cancel_all_orders()
        self.dydx_conn2.cancel_all_orders()

    def create_grid_orders(self, market_price1: float, market_price2: float):
        spread_price = self.get_spread_price(market_price1, market_price2)
        order1_usd_amount = round(
            self.size / market_price1, ndigits=NDIGITS_ETH_AMOUNT_ROUNDING)

        number_of_orders = self.config['trading_parameters']['orders_in_market']
        if self.side == 'long':
            for i in range(1, number_of_orders+1):
                grid_price = spread_price - self.grid_step * i
                instr_1_price = round(
                    grid_price * market_price2, ndigits=NDIGITS_ETH_PRICE_ROUNDING)
                instr_2_price = market_price1 / grid_price
                print(instr_1_price)
                res = self.dydx_conn1.create_limit_order(
                    ORDER_SIDE_BUY, order1_usd_amount, instr_1_price)
                # print(res)
                # break

    async def run(self):
        # removing all previous orders before the start
        self.remove_all_orders()

        timedelta = float(
            self.config['trading_parameters']['refresh_interval_ms'] / 1000)

        while True:
            market_price1 = self.dydx_conn1.get_index_price()
            market_price2 = self.dydx_conn2.get_index_price()

            # spread_price = self.get_spread_price(market_price1, market_price2)

            self.create_grid_orders(market_price1, market_price2)

            # take_profit_price =

            # if self.side == ORDER_SIDE_BUY:
            #     if (self.initial_spread_price - spread_price) >= self.grid_step:
            #         if self.last_triggered_price is None or self.last_triggered_price > spread_price:
            #             res = self.dydx_conn1.create_market_order(
            #                 self.side, self.size)
            #             self.last_triggered_price = spread_price

            # elif self.side == ORDER_SIDE_SELL:
            #     if (spread_price - self.initial_spread_price) >= self.grid_step:
            #         if self.last_triggered_price is None or self.last_triggered_price < spread_price:
            #             self.dydx_conn1.create_market_order(
            #                 self.side, self.size)
            #             self.last_triggered_price = spread_price

            # res = self.dydx_conn1.create_take_profit_order(
            #     ORDER_SIDE_BUY, '0.01', '11')

            # amount = round(self.size / market_price1, 3)
            # rounded_market_price = round(market_price1, 1)
            # print(amount, rounded_market_price)

            # res = self.dydx_conn1.create_limit_order(
            #     self.side, amount, rounded_market_price)

            # res = self.dydx_conn1.get_orders().data

            # print(res)

            # await self.telegram_bot.send_message(message=res)

            time.sleep(timedelta)

            break
