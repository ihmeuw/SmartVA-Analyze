#!/usr/bin/env bash
set -e

if [[ ! -z "$WINE" ]]; then
  WIN_REQUIREMENTS="-r requirements-win.txt"
else
  WIN_REQUIREMENTS=""
fi


$WINE python -m pip install --user -r requirements.txt -r requirements-dev.txt $WIN_REQUIREMENTS

./pkg/build-agent/run_tests.sh
./pkg/build-agent/run_build.sh
