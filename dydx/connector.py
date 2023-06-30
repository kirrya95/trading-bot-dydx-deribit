from dydx3.constants import MARKET_ETH_USD, ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
import time
import logging
from dydx3 import Client
from web3 import Web3

# WEB_PROVIDER_URL = 'http://localhost:8545'
NETWORK_ID_GOERLI = 5
# ETHEREUM_ADDRESS = '0x29FA2F326b01203D8C31852d47f0d053Fc7Ce7E7'
# API_HOST_GOERLI = 'https://api.stage.dydx.exchange'


class dYdXConnection:
    def __init__(self, config):
        self.host = config['platforms']['dydx_testnet']['host']
        self.network_id = NETWORK_ID_GOERLI
        # self.web3 = Web3(Web3.HTTPProvider(WEB_PROVIDER_URL))
        self.eth_private_key = config['eth_private_key']
        self.market = MARKET_ETH_USD

        self.client = Client(
            host=self.host,
            network_id=self.network_id,
            # web3=self.web3,
            eth_private_key=self.eth_private_key,
        )

        stark_private_key = config['stark_private_key']
        # self.client.stark_private_key = self.client.onboarding.derive_stark_key()[
        #     'private_key']
        self.client.stark_private_key = stark_private_key

        account_response = self.client.private.get_account().data
        self.position_id = account_response['account']['positionId']
        # print('position_id', self.position_id)

        # self.create_limit_order(ORDER_SIDE_BUY, '0.001', '10000', '0.0003')
        # self.create_market_order(ORDER_SIDE_BUY, '0.01')

    def create_limit_order(self, side, size, price, limit_fee, post_only=True):
        order_params = {
            'position_id': self.position_id,
            'market': self.market,
            'side': side,
            'order_type': ORDER_TYPE_LIMIT,
            'post_only': post_only,
            'size': size,
            'price': price,
            'limit_fee': limit_fee,
            'expiration_epoch_seconds': time.time() + 5 * 60,
        }

        order_response = self.client.private.create_order(**order_params).data
        # print(order_response)

        return order_response

    def create_market_order(self, side, size):
        if side == ORDER_SIDE_BUY:
            price = '99999999'  # Very high price to execute the order immediately
        elif side == ORDER_SIDE_SELL:
            price = '0.00000001'  # Very low price to execute the order immediately
        else:
            raise ValueError(f"Invalid order side: {side}")

        order_params = {
            'position_id': self.position_id,
            'market': self.market,
            'side': side,
            'order_type': ORDER_TYPE_LIMIT,
            'post_only': False,
            'size': size,
            'price': price,
            'limit_fee': '0.0015',  # Adjust the fee as needed
            'expiration_epoch_seconds': time.time() + 5 * 60,
        }

        order_response = self.client.private.create_order(**order_params).data
        # print(order_response)

        return order_response

    def get_index_price(self):
        response = self.client.public.get_markets().data
        eth_usd_market_data = response['markets'][self.market]
        market_price = eth_usd_market_data['indexPrice']

        return market_price

    # def get_open_orders(self):
    #     return self.client.private.get_orders(status='OPEN')

    # def cancel_order(self, order_id):
    #     return self.client.private.cancel_order(order_id)

    # def get_positions(self):
    #     return self.client.private.get_positions()
