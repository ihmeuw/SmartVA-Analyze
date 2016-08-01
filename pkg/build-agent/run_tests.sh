#!/usr/bin/env bash

set -e

TEST_FILE=$(pwd)/test-results.xml

cd ../smartva

if [[ -f $TEST_FILE ]]; then
    rm $TEST_FILE
fi

PYTHONPATH=. env/Scripts/py.test --junitxml=$TEST_FILE test

if [[ -f $TEST_FILE ]]; then
  exit 0
fi

exit 1
