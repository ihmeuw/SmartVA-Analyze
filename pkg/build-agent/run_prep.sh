#!/usr/bin/env bash

set -e

cd ../smartva

git fetch

if [[ -n $1 ]]; then
    git checkout $1
fi

git pull
