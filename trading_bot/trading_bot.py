import time


from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL


class TradingBot:
    def __init__(self, dydx_conn1, dydx_conn2, telegram_bot, config):
        self.config = config
        self.dydx_conn1 = dydx_conn1
        self.dydx_conn2 = dydx_conn2
        self.telegram_bot = telegram_bot

        self.side = ORDER_SIDE_BUY if config['trading_parameters']['side'] == 'long' else ORDER_SIDE_SELL

        self.initial_market_price1 = self.dydx_conn1.get_index_price()
        self.initial_market_price2 = self.dydx_conn2.get_index_price()

        self.grid_orders = []

    def get_spread_price(self, market_price1, market_price2):
        spread_operator = self.config['trading_parameters']['spread_operator']

        if spread_operator == '/':
            spread_price = market_price1 / market_price2
        elif spread_operator == '*':
            spread_price = market_price1 * market_price2
        elif spread_operator == '+':
            spread_price = market_price1 + market_price2
        elif spread_operator == '-':
            spread_price = market_price1 - market_price2
        else:
            raise ValueError(f"Invalid spread operator: {spread_operator}")

        return spread_price

    def remove_grid_orders(self):
        for order in self.grid_orders:
            self.dydx_conn1.cancel_order(order['id'])
            self.dydx_conn2.cancel_order(order['id'])

    def create_grid_orders(self, spread_price):
        pass

    async def run(self):

        timedelta = float(
            self.config['trading_parameters']['refresh_interval_ms'] / 1000)

        while True:
            # result = self.dydx_connection.create_market_order(
            #     ORDER_SIDE_BUY, '0.01')

            market_price1 = self.dydx_conn1.get_index_price()
            market_price2 = self.dydx_conn2.get_index_price()

            spread_price = self.get_spread_price(market_price1, market_price2)

            res = self.dydx_conn1.create_take_profit_order(
                ORDER_SIDE_BUY, '0.01', '11')

            # res = self.dydx_conn1.get_orders().data

            print(res)

            # await self.telegram_bot.send_message(message=res)

            time.sleep(timedelta)

            break
