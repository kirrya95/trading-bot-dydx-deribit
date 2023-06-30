import time
import logging
from dydx3 import Client
from web3 import Web3

class dYdXConnection:
    def __init__(self, api_key_credentials, stark_private_key=None):
        self.client = Client(
            host='https://api.dydx.exchange',
            api_key_credentials=api_key_credentials,
            stark_private_key=stark_private_key
        )

    def get_price(self, market):
        return self.client.public.get_orderbook(market)

    def create_order(self, market, side, price, amount):
        return self.client.private.create_order(
            market=market,
            side=side,
            price=price,
            amount=amount,
            type='LIMIT',
            postOnly=True
        )

    def get_open_orders(self):
        return self.client.private.get_orders(status='OPEN')

    def cancel_order(self, order_id):
        return self.client.private.cancel_order(order_id)

    def get_positions(self):
        return self.client.private.get_positions()
