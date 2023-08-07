import typing as tp
from constants import GridDirections
from dataclasses import dataclass


@dataclass
class InstrPrices:
    best_bid: float
    best_ask: float


def check_operator(operator: str):
    if operator not in ['/', '*', '+', '-']:
        raise ValueError(f"Invalid spread operator: {operator}")


def calculate_spread_from_two_instr_prices(instr1_bid_ask: InstrPrices,
                                           instr2_bid_ask: InstrPrices,
                                           spread_operator: str,
                                           grid_direction: GridDirections) -> float:
    check_operator(spread_operator)

    if grid_direction == GridDirections.GRID_DIRECTION_LONG:
        instr1_price = instr1_bid_ask.best_ask
        instr2_price = instr2_bid_ask.best_bid
    elif grid_direction == GridDirections.GRID_DIRECTION_SHORT:
        instr1_price = instr1_bid_ask.best_bid
        instr2_price = instr2_bid_ask.best_ask
    else:
        raise ValueError(f"Invalid grid direction: {grid_direction}")

    if spread_operator == '/':
        spread_price = instr1_price / instr2_price
    elif spread_operator == '*':
        spread_price = instr1_price * instr2_price
    elif spread_operator == '+':
        spread_price = instr1_price + instr2_price
    elif spread_operator == '-':
        spread_price = instr1_price - instr2_price
    else:
        raise ValueError(f"Invalid spread operator: {spread_operator}")

    return spread_price
