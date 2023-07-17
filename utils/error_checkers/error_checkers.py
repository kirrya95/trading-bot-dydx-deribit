from functools import wraps

from constants import *


def check_grid_direction():
    def decorator(func):
        @wraps(func)
        async def wrapper(grid_direction, *args, **kwargs):
            if grid_direction not in [GRID_DIRECTION_LONG, GRID_DIRECTION_SHORT]:
                raise ValueError(
                    f'Incorrect side. Should be either {GRID_DIRECTION_LONG} or {GRID_DIRECTION_SHORT}')
            return await func(grid_direction, *args, **kwargs)
        return wrapper
    return decorator


def check_side():
    def decorator(func):
        @wraps(func)
        async def wrapper(side, *args, **kwargs):
            if side not in [ORDER_SIDE_BUY, ORDER_SIDE_SELL]:
                raise ValueError(
                    f'Incorrect side. Should be either {ORDER_SIDE_BUY} or {ORDER_SIDE_SELL}')
            return await func(side, *args, **kwargs)
        return wrapper
    return decorator
