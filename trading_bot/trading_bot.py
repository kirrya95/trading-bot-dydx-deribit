import time


from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL


class TradingBot:
    def __init__(self, dydx_conn1, dydx_conn2, telegram_bot, config):
        self.config = config
        self.dydx_conn1 = dydx_conn1
        self.dydx_conn2 = dydx_conn2
        self.telegram_bot = telegram_bot

    def spread_price(self, market_price1, market_price2):
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

    async def run(self):

        timedelta = float(
            self.config['trading_parameters']['refresh_interval_ms'] / 1000)

        while True:
            # result = self.dydx_connection.create_market_order(
            #     ORDER_SIDE_BUY, '0.01')

            market_price1 = self.dydx_conn1.get_index_price()
            market_price2 = self.dydx_conn2.get_index_price()

            spread_price = self.spread_price(market_price1, market_price2)

            await self.telegram_bot.send_message(message=str(f"""{spread_price}"""))

            time.sleep(timedelta)
