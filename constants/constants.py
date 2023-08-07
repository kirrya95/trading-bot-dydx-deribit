from dataclasses import dataclass
from .deribit_markets import DeribitPerpetualMarkets, DeribitSpotMarkets
from utils import add_get_attributes


NDIGITS_PRICES_ROUNDING = {
    DeribitPerpetualMarkets.BTC_PERPETUAL: 0,
    DeribitPerpetualMarkets.ETH_PERPETUAL: 1,
    DeribitSpotMarkets.ETH_BTC: 4,
    DeribitSpotMarkets.ETH_USDC: 2,
    DeribitSpotMarkets.BTC_USDC: 2
}

NDIGITS_AMOUNTS_ROUNDING = {
    DeribitPerpetualMarkets.BTC_PERPETUAL: 4,
    DeribitPerpetualMarkets.ETH_PERPETUAL: 4,
    DeribitSpotMarkets.ETH_BTC: 4,
    DeribitSpotMarkets.ETH_USDC: 4,
    DeribitSpotMarkets.BTC_USDC: 4
}

# ------------ Order Side ------------


@dataclass
@add_get_attributes
class OrderSides:
    ORDER_SIDE_BUY = 'BUY'
    ORDER_SIDE_SELL = 'SELL'

# ------------ Grid Direction ------------


@dataclass
@add_get_attributes
class GridDirections:
    GRID_DIRECTION_LONG = 'long'
    GRID_DIRECTION_SHORT = 'short'
