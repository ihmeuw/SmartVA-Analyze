#!/usr/bin/env bash

set -e

find -name "*.pyc" -exec rm {} \;

TEST_FILE=$(pwd)/test-results.xml

if [[ -f $TEST_FILE ]]; then
    rm $TEST_FILE
fi

$WINE python -m pytest --junitxml=$TEST_FILE test

if [[ -f $TEST_FILE ]]; then
  exit 0
fi

exit 1
