import time


from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL


class Order:
    id: str
    clientId: int
    accountId: int
    market: str
    side: str
    price: float
    triggerPrice: float or None
    trailingPercent: str or None
    size: str
    # reduceOnlySize: str
    # remainingSize: str
    type: str
    # createdAt: str
    # unfillableAt: str
    expiresAt: str or None
    status: str
    # timeInForce: str
    # postOnly: bool
    # reduceOnly: bool
    # cancelReason: str or None


# {'id': '7a4cfda4d5156e039614002f9f1254577755f6c051e0be022867da70621c34f', 'clientId': '8991923903728052', 'accountId': 'b5d4420a-c040-5950-a834-a32a9d973028', 'market': 'ETH-USD', 'side': 'BUY', 'price': '10', 'triggerPrice': None, 'trailingPercent': None, 'size': '0.01',
#     'reduceOnlySize': None, 'remainingSize': '0.01', 'type': 'LIMIT', 'createdAt': '2023-07-03T01:40:57.843Z', 'unfillableAt': None, 'expiresAt': '2023-07-03T01:45:57.482Z', 'status': 'PENDING', 'timeInForce': 'GTT', 'postOnly': True, 'reduceOnly': False, 'cancelReason': None}


class TradingBot:
    def __init__(self, dydx_conn1, dydx_conn2, telegram_bot, config):
        self.config = config
        self.dydx_conn1 = dydx_conn1
        self.dydx_conn2 = dydx_conn2
        self.telegram_bot = telegram_bot

        self.size = float(config['trading_parameters']['order_size'])
        self.grid_step = float(config['trading_parameters']['grid_step'])
        self.side = ORDER_SIDE_BUY if config['trading_parameters']['side'] == 'long' else ORDER_SIDE_SELL

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
        elif spread_operator == '+':
            spread_price = market_price1 + market_price2
        elif spread_operator == '-':
            spread_price = market_price1 - market_price2
        else:
            raise ValueError(f"Invalid spread operator: {spread_operator}")

        return spread_price

    # TODO: implement
    def get_take_profit_price(self, spread_price: float) -> float:
        self.grid_step
        self.side
        # self.percent

        # return 1 - sum()

    def remove_grid_orders(self):
        # for order in self.grid_orders:
        #     self.dydx_conn1.cancel_order(order['id'])
        #     self.dydx_conn2.cancel_order(order['id'])
        pass

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

            take_profit_price = 

            if self.side == ORDER_SIDE_BUY:
                if (self.initial_spread_price - spread_price) >= self.grid_step:
                    if self.last_triggered_price is None or self.last_triggered_price > spread_price:
                        res = self.dydx_conn1.create_market_order(
                            self.side, self.size)
                        self.last_triggered_price = spread_price
            # if self.side == ORDER_SIDE_SELL:
            #     if (spread_price - self.initial_spread_price) >= self.grid_step:
            #         if self.last_triggered_price is None or self.last_triggered_price < spread_price:
            #             self.dydx_conn1.create_market_order(
            #                 self.side, self.size)
            #             self.last_triggered_price = spread_price

            # res = self.dydx_conn1.create_take_profit_order(
            #     ORDER_SIDE_BUY, '0.01', '11')

            # res = self.dydx_conn1.get_orders().data

            # print(res)

            # await self.telegram_bot.send_message(message=res)

            time.sleep(timedelta)

            break
