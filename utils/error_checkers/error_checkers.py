from functools import wraps
import inspect

from constants import *


def check_grid_direction(func):
    sig = inspect.signature(func)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        grid_direction = bound.arguments.get('grid_direction')
        if grid_direction is None:
            raise ValueError('Grid direction is not specified (None)')
        if grid_direction not in [GridDirections.GRID_DIRECTION_LONG, GridDirections.GRID_DIRECTION_SHORT]:
            raise ValueError(
                f'Incorrect direction. Should be either {GridDirections.GRID_DIRECTION_LONG} or {GridDirections.GRID_DIRECTION_SHORT}')
        return await func(*args, **kwargs)
    return wrapper


def check_side(func):
    sig = inspect.signature(func)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        side = bound.arguments.get('side')
        side = side.upper()
        if side not in [OrderSides.ORDER_SIDE_BUY, OrderSides.ORDER_SIDE_SELL]:
            raise ValueError(
                f'Incorrect side. Should be either {OrderSides.ORDER_SIDE_BUY} or {OrderSides.ORDER_SIDE_SELL}')
        return await func(*args, **kwargs)
    return wrapper
