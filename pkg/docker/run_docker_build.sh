#!/usr/bin/env bash
set -e

cd ~
cp -r smartva/pkg/build-agent/. build-agent/
cp smartva/pkg/docker/run_tests_and_build_in_wine.patch .
git apply run_tests_and_build_in_wine.patch

wine python -m pip install -U \
      -r smartva/requirements.txt \
      -r smartva/requirements-dev.txt \
      -r smartva/requirements-win.txt

cd build-agent
./run_tests.sh
./run_build.sh
