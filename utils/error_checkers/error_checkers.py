from functools import wraps

from constants import *


def check_grid_direction():
    def decorator(func):
        @wraps(func)
        async def wrapper(grid_direction, *args, **kwargs):
            if grid_direction not in [GridDirections.GRID_DIRECTION_LONG, GridDirections.GRID_DIRECTION_SHORT]:
                raise ValueError(
                    f'Incorrect side. Should be either {GridDirections.GRID_DIRECTION_LONG} or {GridDirections.GRID_DIRECTION_SHORT}')
            return await func(grid_direction, *args, **kwargs)
        return wrapper
    return decorator


def check_side():
    def decorator(func):
        @wraps(func)
        async def wrapper(side, *args, **kwargs):
            if side not in [OrderSides.ORDER_SIDE_BUY, OrderSides.ORDER_SIDE_SELL]:
                raise ValueError(
                    f'Incorrect side. Should be either {OrderSides.ORDER_SIDE_BUY} or {OrderSides.ORDER_SIDE_SELL}')
            return await func(side, *args, **kwargs)
        return wrapper
    return decorator
