#!/usr/bin/env bash

set -e

find -name "*.pyc" -exec rm {} \;

TEST_FILE=$(pwd)/test-results.xml

if [[ -f $TEST_FILE ]]; then
    rm $TEST_FILE
fi

CURRENT_TAG=$(git log --tags --simplify-by-decoration --pretty="%d" | grep -oP "(?<=\().+(?=\))" | head -1)
DATA_CHANGED=$(git diff --name-only $CURRENT_TAG..HEAD | grep "\.csv" | wc -l)
if [[ $DATA_CHANGED -gt 0 ]]; then
    PYTEST_FLAGS="--data-checks"
else
    PYTEST_FLAGS=""
fi

$WINE python -m pytest --junitxml=$TEST_FILE $PYTEST_FLAGS test

if [[ -f $TEST_FILE ]]; then
  exit 0
fi

exit 1
