import typing as tp
from constants import DeribitAvailableKinds, DeribitSpotMarkets
from constants import GridDirections, OrderSides, NDIGITS_AMOUNTS_ROUNDING
from utils import InstrPrices


def get_size_to_trade(instr_name: str,
                      instr_prices: InstrPrices,
                      direction: GridDirections,
                      kind: str,
                      config_size: float):
    """
    Function takes into account that for futures market size is in USD,
    but for spot market size is in base currency (e.g. BTC for BTC/USDC market)

    Returns:
        size (float): size to trade in <base or stablecoin> currency
    """

    side = OrderSides.ORDER_SIDE_BUY if direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_SELL

    if kind == 'future':
        size = config_size
        return round(size, ndigits=NDIGITS_AMOUNTS_ROUNDING[instr_name])

    if kind == DeribitAvailableKinds.SPOT:
        if side == OrderSides.ORDER_SIDE_BUY:
            size = config_size / instr_prices.best_ask
            if instr_name == DeribitSpotMarkets.ETH_BTC:
                return round(size, ndigits=NDIGITS_AMOUNTS_ROUNDING[DeribitSpotMarkets.ETH_USDC])
            else:
                return round(size, ndigits=NDIGITS_AMOUNTS_ROUNDING[DeribitSpotMarkets.ETH_USDC])
        elif side == OrderSides.ORDER_SIDE_SELL:
            size = config_size / instr_prices.best_bid
            if instr_name == DeribitSpotMarkets.ETH_BTC:
                return round(size, ndigits=NDIGITS_AMOUNTS_ROUNDING[DeribitSpotMarkets.BTC_USDC])
            else:
                return round(size, ndigits=NDIGITS_AMOUNTS_ROUNDING[DeribitSpotMarkets.ETH_USDC])

    raise ValueError('Incorrect kind. Should be either future or spot')
