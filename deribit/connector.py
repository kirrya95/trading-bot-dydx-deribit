import websocket
import json
import base64
import hashlib
import time
import hmac


class DeribitConnection:
    def __init__(self, client_id, client_secret):
        # используйте "wss://www.deribit.com/ws/api/v2" для реального режима
        self.ws = websocket.create_connection(
            "wss://test.deribit.com/ws/api/v2")
        self.client_id = client_id
        self.client_secret = client_secret
        self._authenticate()

    def _authenticate(self):
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

        self.ws.send(json.dumps(message))
        result = json.loads(self.ws.recv())
        # print(result)
        if 'result' in result and 'access_token' in result['result']:
            self.access_token = result['result']['access_token']
        else:
            raise Exception("Authentication failed: " + str(result))

    def get_contract_size(self, instrument_name):
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

        self.ws.send(json.dumps(message))
        result = json.loads(self.ws.recv())
        if 'result' in result:
            for instrument in result['result']:
                if instrument['instrument_name'] == instrument_name:
                    return instrument['contract_size']

        return None

    def get_asset_price(self, instrument_name,
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

        self.ws.send(json.dumps(message))
        result = json.loads(self.ws.recv())

        if 'result' in result and 'best_bid_price' in result['result'] and 'best_ask_price' in result['result']:
            # return result['result']['best_bid_price'] if action == 'bid' else result['result']['best_ask_price']
            return (result['result']['best_bid_price'], result['result']['best_ask_price'])
        else:
            return None

    def create_limit_order(self, instrument_name, amount, price, action):
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

        self.ws.send(json.dumps(message))
        result = json.loads(self.ws.recv())

        # print(result)

        if 'result' in result and 'order' in result['result']:
            return result['result']['order']
        else:
            return None

    def cancel_all_orders(self):
        pass
