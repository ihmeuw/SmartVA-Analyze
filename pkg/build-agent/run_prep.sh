#!/usr/bin/env bash

set -e

cd ../smartva

find -name "*.pyc" -exec rm {} \;

git fetch

if [[ -n $1 ]]; then
    git checkout $1
fi

git pull
