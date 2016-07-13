from smartva.rules import anemia

BASE_ROW = {
    'g5_02': 2.0,
    'g5_04a': 13.0,
    'a3_07': 1.0,
    'a3_08': 91.0,
    'a3_10': 1.0,
    'a3_17': 1.0,
    'a3_18': 1.0,
    'a2_20': 1.0,
    'a2_37': 1.0,
    'a2_40': 1.0,
    'a2_43': 1.0,
    'a2_69': 1.0,
}


def test_logic_pass():
    assert anemia.logic_rule(BASE_ROW) == anemia.CAUSE_ID


def test_logic_fail_age():
    row = BASE_ROW.copy()
    row.update({
        'g5_04a': 12.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        'g5_02': 1.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_pregnant():
    row = BASE_ROW.copy()
    row.update({
        'a3_10': 0.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_period1():
    row = BASE_ROW.copy()
    row.update({
        'a3_07': 0.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_period2():
    row = BASE_ROW.copy()
    row.update({
        'a3_08': 90.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_pass_postpartum1():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': 1.0,
        'a3_18': 0.0,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_pass_postpartum2():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': 0.0,
        'a3_18': 1.0,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_fail_postpartum1():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': 0.0,
        'a3_18': 0.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_pass_symptoms1():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': 1.0,
        'a2_37': 1.0,
        'a2_40': 0.0,
        'a2_43': 1.0,
        'a2_69': 0.0,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_fail_symptoms1():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': 0.0,
        'a2_37': 0.0,
        'a2_40': 0.0,
        'a2_43': 0.0,
        'a2_69': 0.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_symptoms2():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': 1.0,
        'a2_37': 0.0,
        'a2_40': 0.0,
        'a2_43': 0.0,
        'a2_69': 0.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_symptoms3():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': 1.0,
        'a2_37': 1.0,
        'a2_40': 0.0,
        'a2_43': 0.0,
        'a2_69': 0.0,
    })

    assert anemia.logic_rule(row) is False
