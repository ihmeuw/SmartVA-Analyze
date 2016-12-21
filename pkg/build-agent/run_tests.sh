#!/usr/bin/env bash

set -e

cd ../smartva

find -name "*.pyc" -exec rm {} \;

TEST_FILE=$(pwd)/test-results.xml

if [[ -f $TEST_FILE ]]; then
    rm $TEST_FILE
fi

PYTHONPATH=. env/Scripts/py.test --junitxml=$TEST_FILE test

if [[ -f $TEST_FILE ]]; then
  exit 0
fi

exit 1
