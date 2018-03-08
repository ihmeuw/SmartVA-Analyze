#!/usr/bin/env bash

set -e

for BUILD_OS in win linux; do
  TAG="smartva-build-$BUILD_OS"
  docker build \
      -t $TAG \
      -f ./pkg/docker/$BUILD_OS-build/Dockerfile \
      ./pkg/docker
  docker run --rm -v `pwd`:/home/smartva/smartva $TAG
done
