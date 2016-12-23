#!/usr/bin/env bash

set -e

cp ./pkg/docker/Dockerfile .

docker build -t smartva-build .
docker run --rm -v `pwd`:/home/smartva/smartva smartva-build
