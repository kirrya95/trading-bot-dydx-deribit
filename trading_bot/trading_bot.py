from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL


class TradingBot:
    def __init__(self, dydx_conn1, dydx_conn2, telegram_bot, config):
        self.config = config
        self.dydx_conn1 = dydx_conn1
        self.dydx_conn2 = dydx_conn2
        self.telegram_bot = telegram_bot

    # def

    async def run(self):

        while True:
            # result = self.dydx_connection.create_market_order(
            #     ORDER_SIDE_BUY, '0.01')

            market_price1 = self.dydx_conn1.get_index_price()
            market_price2 = self.dydx_conn2.get_index_price()

            await self.telegram_bot.send_message(message=str(f"""{market_price1},
                                                             \n {market_price2}"""))

            break
