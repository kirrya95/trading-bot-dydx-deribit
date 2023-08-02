from utils import GridDirections


def get_side_from_direction(direction):
    if direction == GridDirections.GRID_DIRECTION_LONG:
        return 'buy'
    elif direction == GridDirections.GRID_DIRECTION_SHORT:
        return 'sell'
    else:
        raise ValueError('Invalid grid direction')


def get_direction_from_side(side):
    if side == 'buy':
        return GridDirections.GRID_DIRECTION_LONG
    elif side == 'sell':
        return GridDirections.GRID_DIRECTION_SHORT
    else:
        raise ValueError('Invalid grid direction')


def get_opposite_direction(direction):
    if direction == GridDirections.GRID_DIRECTION_LONG:
        return GridDirections.GRID_DIRECTION_SHORT
    elif direction == GridDirections.GRID_DIRECTION_SHORT:
        return GridDirections.GRID_DIRECTION_LONG
    else:
        raise ValueError('Invalid grid direction')


def get_opposite_side(side):
    if side == 'buy':
        return 'sell'
    elif side == 'sell':
        return 'buy'
    else:
        raise ValueError('Invalid grid direction')


def get_side_price_from_dict_prices(instr_prices, side):
    if 'best_ask' not in instr_prices.keys() or 'best_bid' not in instr_prices.keys():
        raise ValueError(
            'Invalid dictionary with prices. Should contain keys "best_ask" and "best_bid"')

    if side == 'buy':
        return instr_prices['best_ask']
    elif side == 'sell':
        return instr_prices['best_bid']
    else:
        raise ValueError('Invalid side')
