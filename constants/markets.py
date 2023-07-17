from dataclasses import dataclass


def add_get_attributes(cls):
    def get_attributes():
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__') and not callable(v)}

    cls.get_attributes = get_attributes
    return cls


@dataclass
@add_get_attributes
class DeribitPerpetualMarkets():
    BTC_PERPETUAL = 'BTC-PERPETUAL'
    BTC_USDC_PERPETUAL = 'BTC_USDC-PERPETUAL'

    ETH_PERPETUAL = 'ETH-PERPETUAL'
    ETH_USDC_PERPETUAL = 'ETH_USDC-PERPETUAL'


@dataclass
@add_get_attributes
class DeribitSpotMarkets():
    BTC_USDC = 'BTC_USDC'
    ETH_USDC = 'ETH_USDC'
    ETH_BTC = 'ETH_BTC'


if __name__ == '__main__':
    print(DeribitPerpetualMarkets.get_attributes())
    print(DeribitSpotMarkets.get_attributes())
