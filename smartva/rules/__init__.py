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
    'malnutrition',
    'measles',
    'other_injury_adult',
    'other_injury_child',
    'other_pregnancy',
    'poisoning_adult',
    'poisoning_child',
    'road_traffic_adult',
    'road_traffic_child',
    'sepsis',
    'suicide',
    'tetanus_neonate',
]

from . import *


def modules():
    return [globals().get(name) for name in __all__]
