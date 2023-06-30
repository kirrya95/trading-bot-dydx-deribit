import time
import logging
from dydx3 import Client
from web3 import Web3

WEB_PROVIDER_URL = 'http://localhost:8545'
NETWORK_ID_GOERLI = 5
# ETHEREUM_ADDRESS = '0x29FA2F326b01203D8C31852d47f0d053Fc7Ce7E7'
# API_HOST_GOERLI = 'https://api.stage.dydx.exchange'

from dydx3.constants import MARKET_BTC_USD, ORDER_SIDE_BUY, ORDER_TYPE_LIMIT


class dYdXConnection:
    def __init__(self, config):
        self.client = Client(
            host=config['platforms']['dydx_testnet']['host'],
            network_id=NETWORK_ID_GOERLI,
            web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
            eth_private_key=config['eth_private_key'],
        )
        self.client.stark_private_key = self.client.onboarding.derive_stark_key()['private_key']

        print('stark_private_key', self.client.stark_private_key)

        account_response = self.client.private.get_account().data
        position_id = account_response['account']['positionId']
        print('position_id', position_id)


        # Post an bid at a price that is unlikely to match.
        order_params = {
            'position_id': position_id,
            'market': MARKET_BTC_USD,
            'side': ORDER_SIDE_BUY,
            'order_type': ORDER_TYPE_LIMIT,
            'post_only': True,
            'size': '0.0777',
            'price': '20',
            'limit_fee': '0.0015',
            'expiration_epoch_seconds': time.time() + 5 * 60,
        }
        order_response = self.client.private.create_order(**order_params).data
        # order_id = order_response['order']['id']
        print(order_response)

    # def create_dydx_client(self):
    #     auth = AuthCredentials(
    #         api_key=self.config['api_keys']['dydx']['api_key'],
    #         api_secret=self.config['api_keys']['dydx']['api_secret']
    #     )
    #     return Client(host='https://api.stage.dydx.exchange', auth=auth)

    def test(self):
        return self.client.private.get_account()

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
