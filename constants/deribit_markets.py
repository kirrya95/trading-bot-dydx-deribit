from dataclasses import dataclass
from utils import add_get_attributes

@dataclass
@add_get_attributes
class DeribitPerpetualMarkets:
    BTC_PERPETUAL = 'BTC-PERPETUAL'
    BTC_USDC_PERPETUAL = 'BTC_USDC-PERPETUAL'

    ETH_PERPETUAL = 'ETH-PERPETUAL'
    ETH_USDC_PERPETUAL = 'ETH_USDC-PERPETUAL'


@dataclass
@add_get_attributes
class DeribitSpotMarkets:
    BTC_USDC = 'BTC_USDC'
    ETH_USDC = 'ETH_USDC'
    ETH_BTC = 'ETH_BTC'


if __name__ == '__main__':
    print(DeribitPerpetualMarkets.get_attributes())
    print(DeribitSpotMarkets.get_attributes())
