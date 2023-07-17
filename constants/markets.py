from dataclasses import dataclass


@dataclass
class DeribitPerpetualMarkets:
    BTC_PERPETUAL = 'BTC-PERPETUAL'
    BTC_USDC_PERPETUAL = 'BTC_USDC-PERPETUAL'

    ETH_PERPETUAL = 'ETH-PERPETUAL'
    ETH_USDC_PERPETUAL = 'ETH_USDC-PERPETUAL'


@dataclass
class DeribitSpotMarkets:
    BTC_USDC = 'BTC_USDC'
    ETH_USDC = 'ETH_USDC'
    ETH_BTC = 'ETH_BTC'



if __name__ == '__main__':
    attributes = {k: v for k, v in DeribitSpotMarkets.__dict__.items() if not k.startswith('__')}
    print(attributes)
