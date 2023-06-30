import time
import logging
from dydx3 import Client
from web3 import Web3

WEB_PROVIDER_URL = 'http://localhost:8545'
NETWORK_ID_GOERLI = 5
ETHEREUM_ADDRESS = '0x29FA2F326b01203D8C31852d47f0d053Fc7Ce7E7'
API_HOST_GOERLI = 'https://api.stage.dydx.exchange'


class dYdXConnection:
    def __init__(self, config):
        # self.client = Client(
        #     host=config['platforms']['dydx_testnet']['host'],
        #     # api_key_credentials=api_key_credentials,
        #     eth_private_key=config['eth_private_key'],
        # )
        # self.client = Client(
        #     network_id=NETWORK_ID_GOERLI,
        #     host=API_HOST_GOERLI,
        #     default_ethereum_address=ETHEREUM_ADDRESS,
        #     web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
        # )
        self.client = Client(
            host=WEB_PROVIDER_URL,
            # stark_private_key=stark_private_key,
            eth_private_key=config['eth_private_key'],
        )
        # print('here')

        print(self.client.onboarding.derive_stark_key())

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
