import websocket
import json
import base64
import hashlib
import time
import hmac

import asyncio
import websockets
import json


class DeribitConnection:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def connect(self):
        self.connection = await websockets.client.connect('wss://test.deribit.com/ws/api/v2')

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
            print(
                f"Failed to cancel order {order_id}: {cancel_result['error']}")

    async def cancel_all_orders(self, instrument_name):
        get_orders_message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "private/get_open_orders_by_currency",
            "params": {
                "currency": instrument_name.split("-")[0],
                "kind": "option" if 'option' in instrument_name else "future",
            }
        }

        await self.connection.send(json.dumps(get_orders_message))
        response = await self.connection.recv()
        result = json.loads(response)

        if 'result' in result:
            cancel_tasks = [self.cancel_order(
                order['order_id']) for order in result['result']]
            # await asyncio.gather(*cancel_tasks)
            for task in cancel_tasks:
                await task
        else:
            print(
                f"Failed to get open orders: {result['error'] if 'error' in result else 'Unknown error'}")

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

        return None

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
            return None

    async def create_limit_order(self, instrument_name, amount, price, action):
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
            return None
