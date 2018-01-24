import json
import os

import pytest

from smartva.config import basedir
from smartva.data.adult_tariff_data import (
    SYMPTOM_DESCRIPTIONS as ADULT_SYMPTOM_DESCRIPTIONS,
    CAUSES as ADULT_CAUSES,
    CAUSES46 as ADULT_CAUSES46,
)
from smartva.data.child_tariff_data import (
    SYMPTOM_DESCRIPTIONS as CHILD_SYMPTOM_DESCRIPTIONS,
    CAUSES as CHILD_CAUSES,
    CAUSES46 as CHILD_CAUSES46,
)
from smartva.data.neonate_tariff_data import (
    SYMPTOM_DESCRIPTIONS as NEONATE_SYMPTOM_DESCRIPTIONS,
    CAUSES as NEONATE_CAUSES,
    CAUSES46 as NEONATE_CAUSES46,
)

LANGUAGES = ('chinese', 'spanish')


@pytest.fixture(params=LANGUAGES, scope='module')
def translation(request):
    path = os.path.join(basedir, 'data', '{}.json'.format(request.param))
    with open(path, 'rb') as f:
        return json.load(f)


def test_symptom_descriptions(translation):
    english = set()
    english.update(ADULT_SYMPTOM_DESCRIPTIONS.values())
    english.update(CHILD_SYMPTOM_DESCRIPTIONS.values())
    english.update(NEONATE_SYMPTOM_DESCRIPTIONS.values())

    diff = english.difference(translation['symptoms'].keys())
    extra = set(translation['symptoms'].keys()).difference(english)

    assert not diff and not extra


def test_causes(translation):
    english = set()
    english.update(ADULT_CAUSES.values())
    english.update(ADULT_CAUSES46.values())
    english.update(CHILD_CAUSES.values())
    english.update(CHILD_CAUSES46.values())
    english.update(NEONATE_CAUSES.values())
    english.update(NEONATE_CAUSES46.values())

    diff = english.difference(translation['causes'].keys())

    assert not diff
