__all__ = [
    'anemia',
    'bite_adult',
    'bite_child',
    'cancer_child',
    'drowning_adult',
    'drowning_child',
    'falls_adult',
    'falls_child',
    'fires_adult',
    'fires_child',
    'hemorrhage',
    'homicide_adult',
    'homicide_child',
    'hypertensive',
]

from . import *


def modules():
    return [globals().get(name) for name in __all__]
