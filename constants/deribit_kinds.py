from dataclasses import dataclass

from utils import add_get_attributes


@dataclass
@add_get_attributes
class DeribitAvailableKinds:
    PERPETUAL = 'future'
    SPOT = 'spot'
