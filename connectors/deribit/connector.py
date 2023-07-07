import json
import base64
import hashlib
import time
import hmac
import asyncio
import websockets

from connectors import AbstractConnector
from utils import load_config

config = load_config('config.yaml')


class DeribitConnection(AbstractConnector):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def connect(self):
        if config['trading_parameters']['mainnet'] == False:
            self.connection = await websockets.client.connect(config['platforms']['deribit_testnet']['websocket_url'])
        if config['trading_parameters']['mainnet'] == True:
            self.connection = await websockets.client.connect(config['platforms']['deribit_mainnet']['websocket_url'])

        return "Connected to Deribit"

    async def authenticate(self):
        message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        }
        await self.connection.send(json.dumps(message))
        response = await self.connection.recv()
        result = json.loads(response)
        if 'result' in result and 'access_token' in result['result']:
            self.access_token = result['result']['access_token']
        else:
            raise Exception("Authentication failed: " + str(result))

        return "Authenticated"

    async def get_currency_from_instrument(self, instrument_name):
        if 'DVOL' not in instrument_name:
            currency = instrument_name.split('-')[0]
        else:
            raise ValueError(
                f"DVOL currently is not supported. {instrument_name}")
        return currency

    # async def subscribe_to_order_updates(self):
    #     channel = "user.orders.any.any"
    #     message = {
    #         "jsonrpc": "2.0",
    #         "id": 42,  # can be any number
    #         "method": "public/subscribe",
    #         "params": {
    #             "channels": [channel]
    #         }
    #     }

    #     await self.connection.send(json.dumps(message))

    # async def start_listening(self):
    #     await self.subscribe_to_order_updates()

    #     # while True:
    #     message = await self.connection.recv()
    #     message_data = json.loads(message)
    #     if 'params' in message_data:
    #         data = message_data['params']['data']
    #         if data['order_state'] == 'filled':
    #             print(f"Order {data['order_id']} was filled.")

    async def get_all_orders(self, currency, instrument_name):
        get_orders_message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "private/get_open_orders_by_currency",
            "params": {
                "currency": currency,
                "kind": "option" if 'option' in instrument_name else "future",
            }
        }

        await self.connection.send(json.dumps(get_orders_message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result:
            return result['result']
        else:
            raise ValueError(
                f"Failed to get open orders: {result['error']}")

    async def cancel_order(self, order_id):
        cancel_order_message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "private/cancel",
            "params": {
                "order_id": order_id
            }
        }

        await self.connection.send(json.dumps(cancel_order_message))
        response = await self.connection.recv()
        cancel_result = json.loads(response)

        if 'error' in cancel_result:
            raise ValueError(
                f"Failed to cancel order {order_id}: {cancel_result['error']}")

        return cancel_result

    async def cancel_all_orders(self, instrument_name):

        orders = await self.get_all_orders(currency=instrument_name.split()[0],
                                           instrument_name=instrument_name)

        cancel_tasks = [self.cancel_order(
            order['order_id']) for order in orders]
        # await asyncio.gather(*cancel_tasks)
        for task in cancel_tasks:
            await task

        return "All limit orders cancelled"

    async def get_contract_size(self, instrument_name):
        message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "public/get_instruments",
            "params": {
                # валюта, которую вы хотите торговать
                "currency": instrument_name.split("-")[0],
                # вид инструмента, будь то опцион или фьючерс
                "kind": "option" if 'option' in instrument_name else "future",
                "expired": False  # фильтрация только активных инструментов
            }
        }

        await self.connection.send(json.dumps(message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result:
            for instrument in result['result']:
                if instrument['instrument_name'] == instrument_name:
                    return instrument['contract_size']
        else:
            raise ValueError(
                f"Failed to get contract size: {result['error'] if 'error' in result else 'Unknown error'}")

        raise ValueError("Failed to get contract size: Instrument not found")

    async def get_asset_price(self, instrument_name,
                              # action
                              ):
        # if action not in ['bid', 'ask']:
        #     raise ValueError(
        #         'Invalid action. Please choose either "bid" or "ask".')

        message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "public/ticker",
            "params": {
                "instrument_name": instrument_name
            }
        }

        await self.connection.send(json.dumps(message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result and 'best_bid_price' in result['result'] and 'best_ask_price' in result['result']:
            # return result['result']['best_bid_price'] if action == 'bid' else result['result']['best_ask_price']
            return (result['result']['best_bid_price'], result['result']['best_ask_price'])
        else:
            raise ValueError(
                f"Failed to get asset price: {result['error'] if 'error' in result else 'Unknown error'}")

    async def create_limit_order(self, instrument_name, amount, price, action):
        action = action.lower()
        if action not in ['buy', 'sell']:
            raise ValueError(
                'Invalid action. Please choose either "buy" or "sell".')

        message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "private/" + action,
            "params": {
                "instrument_name": instrument_name,
                "amount": amount,
                "price": price,
                "type": "limit"
            }
        }

        await self.connection.send(json.dumps(message))
        response = await self.connection.recv()
        result = json.loads(response)
        # print(result)

        if 'result' in result and 'order' in result['result']:
            return result['result']['order']
        else:
            raise ValueError(
                f"Failed to create limit order: {result['error'] if 'error' in result else 'Unknown error'}")

    async def execute_market_order(self, instrument_name, amount, side):
        side = side.lower()

        if side not in ['buy', 'sell']:
            raise ValueError(
                'Invalid side. Please choose either "buy" or "sell".')

        market_order_message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": f"private/{side}",
            "params": {
                "instrument_name": instrument_name,
                "amount": amount,
                "type": "market"
            }
        }
        await self.connection.send(json.dumps(market_order_message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result:
            return result['result']['order']
        else:
            raise ValueError(
                f"Failed to execute market order: {result['error'] if 'error' in result else 'Unknown error'}")

    async def get_position(self, currency, instrument_name) -> float:
        get_positions_message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "private/get_positions",
            "params": {
                "currency": currency
            }
        }
        await self.connection.send(json.dumps(get_positions_message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result:
            for position in result['result']:
                if position['instrument_name'] == instrument_name:
                    print(
                        f"Position size for {instrument_name}: {position['size']}")
                    return float(position['size'])

            print(f"No open position found for {instrument_name}")
            return 0.0
        else:
            raise ValueError(
                f"Failed to get positions: {result['error'] if 'error' in result else 'Unknown error'}")
