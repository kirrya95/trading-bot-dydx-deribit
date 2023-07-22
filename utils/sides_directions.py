from utils import GridDirections


def get_side_from_direction(direction):
    if direction == GridDirections.GRID_DIRECTION_LONG:
        return 'long'
    elif direction == GridDirections.GRID_DIRECTION_SHORT:
        return 'short'
    else:
        raise ValueError('Invalid grid direction')


def get_direction_from_side(side):
    if side == 'long':
        return GridDirections.GRID_DIRECTION_LONG
    elif side == 'short':
        return GridDirections.GRID_DIRECTION_SHORT
    else:
        raise ValueError('Invalid grid direction')
