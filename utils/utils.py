import pytz

from datetime import datetime, timedelta
from utils import GridDirections


# example: datetime.strptime("2023-07-01 00:00:00", "%Y-%m-%d %H:%M:%S")
def to_utc_timestamp(string_datetime):
    dt = datetime.strptime(string_datetime, "%Y-%m-%d %H:%M:%S")
    dt = pytz.UTC.localize(dt)

    return dt.timestamp()


def timedelta_to_str(seconds_difference):
    return timedelta(seconds=seconds_difference)


### DATACLASS MODIFIERS ###

def add_get_attributes(cls):
    def get_attributes():
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__') and not callable(v)}

    cls.get_attributes = get_attributes
    return cls


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


if __name__ == '__main__':
    print(to_utc_timestamp("2023-07-01 00:00:00"))
