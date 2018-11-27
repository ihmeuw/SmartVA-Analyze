#!/usr/bin/env bash

set -e

find -name "*.pyc" -exec rm {} \;

rm -rf build

echo "Building: $BUILD_SPECS"

for SPEC in $BUILD_SPECS; do
  if [[ -z "$WINE" ]]; then
    BUILD_OS="linux"
  else
    BUILD_OS="win"
  fi

  if [[ "$SPEC" == "gui" ]]; then
    BUILD_OPTS="--windowed"
    SPEC_FILE="smartva-$BUILD_OS.spec"
  else
    BUILD_OPTS=""
    SPEC_FILE="smartva-$BUILD_OS-cli.spec"
  fi

  BUILD_TARGET=$(grep name pkg/$SPEC_FILE | tr "'" " " | awk '{print $2}')
  rm -rf dist/$BUILD_TARGET

  cp pkg/$SPEC_FILE .

  $WINE python -m PyInstaller $SPEC_FILE --onefile --clean $BUILD_OPTS

  rm $SPEC_FILE

  if [[ ! -f "./dist/$BUILD_TARGET" ]]; then
    echo "Failed to build $BUILD_TARGET"
    exit 1
  fi
done
