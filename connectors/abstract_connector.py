from abc import ABC, abstractmethod


class AbstractConnector(ABC):
    # @abstractmethod
    # async def get_open_orders(self, instrument_name):
    #     pass

    @abstractmethod
    async def cancel_order(self, order_id):
        pass

    @abstractmethod
    async def cancel_all_orders(self, instrument_name, kind):
        pass

    @abstractmethod
    async def get_contract_size(self, instrument_name):
        pass

    @abstractmethod
    async def get_asset_price(self, instrument_name) -> dict:
        pass

    @abstractmethod
    async def create_limit_order(self, instrument_name, amount, price, action):
        pass

    # @abstractmethod
    # async def execute_market_order(self, instrument_name):
    #     pass
