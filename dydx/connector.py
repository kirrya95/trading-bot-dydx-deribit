from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_TAKE_PROFIT, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
import time
from dydx3 import Client
from web3 import Web3


class dYdXConnection:
    def __init__(self, instrument, config):
        self.config = config
        self.host = config['platforms']['dydx_testnet']['host']
        self.network_id = config['platforms']['dydx_testnet']['network_id']
        self.eth_private_key = config['credentials']['eth_private_key']

        self.market = instrument + '-USD'
        self.limit_fee = config['trading_parameters']['limit_fee']

        self.client = Client(
            host=self.host,
            network_id=self.network_id,
            # web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
            eth_private_key=self.eth_private_key,
        )
        stark_private_key = config['credentials']['stark_private_key']
        # self.client.stark_private_key = self.client.onboarding.derive_stark_key()[
        #     'private_key']
        self.client.stark_private_key = stark_private_key

        account_response = self.client.private.get_account().data
        self.position_id = account_response['account']['positionId']

        # self.create_limit_order(ORDER_SIDE_BUY, '0.001', '10000', '0.0003')
        # self.create_market_order(ORDER_SIDE_BUY, '0.01')

    def create_limit_order(self, side, size, price, post_only=True):
        limit_order_expiration_delay_seconds = self.config[
            'trading_parameters']['limit_order_expiration_delay_seconds']

        order_params = {
            'position_id': self.position_id,
            'market': self.market,
            'side': side,
            'order_type': ORDER_TYPE_LIMIT,
            'post_only': post_only,
            'size': size,
            'price': price,
            'limit_fee': self.limit_fee,
            'expiration_epoch_seconds': time.time() + limit_order_expiration_delay_seconds,
        }

        order_response = self.client.private.create_order(**order_params).data

        return order_response

    def create_take_profit_order(self, side, size, price, post_only=True):
        limit_order_expiration_delay_seconds = self.config[
            'trading_parameters']['limit_order_expiration_delay_seconds']

        order_params = {
            'position_id': self.position_id,
            'market': self.market,
            'side': side,
            'order_type': ORDER_TYPE_TAKE_PROFIT,
            'post_only': post_only,
            'size': size,
            'price': price,
            'trigger_price': price,
            'limit_fee': self.limit_fee,
            'expiration_epoch_seconds': time.time() + limit_order_expiration_delay_seconds,
        }

        order_response = self.client.private.create_order(**order_params).data

        return order_response

    def create_market_order(self, side, size):
        if side == ORDER_SIDE_BUY:
            price = '99999999'  # Very high price to execute the order immediately
        elif side == ORDER_SIDE_SELL:
            price = '0.00000001'  # Very low price to execute the order immediately
        else:
            raise ValueError(f"Invalid order side: {side}")

        limit_order_expiration_delay_seconds = self.config[
            'trading_parameters']['limit_order_expiration_delay_seconds']

        order_params = {
            'position_id': self.position_id,
            'market': self.market,
            'side': side,
            'order_type': ORDER_TYPE_LIMIT,
            'post_only': False,
            'size': size,
            'price': price,
            'limit_fee': '0.0015',  # Adjust the fee as needed
            'expiration_epoch_seconds': time.time() + limit_order_expiration_delay_seconds,
        }

        order_response = self.client.private.create_order(**order_params).data
        # print(order_response)

        return order_response

    def get_index_price(self) -> float:
        response = self.client.public.get_markets().data
        eth_usd_market_data = response['markets'][self.market]
        market_price = eth_usd_market_data['indexPrice']

        return float(market_price)

    def get_orders(self):
        return self.client.private.get_orders(
            market=self.market,
            # status=ORDER_STATUS_OPEN,
            # side=ORDER_SIDE_SELL,
            # type=ORDER_TYPE_LIMIT,
            # limit=50,
        )

    # def get_open_orders(self):
    #     return self.client.private.get_orders(status='OPEN')

    def cancel_order(self, order_id):
        return self.client.private.cancel_order(order_id)

    # def get_positions(self):
    #     return self.client.private.get_positions()
