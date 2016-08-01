#!/usr/bin/env bash

set -e

cd ../smartva

rm -rf build
rm -rf dist
find ./smartva -name "*.pyc" -exec rm {} \;

env/Scripts/pyinstaller.exe smartva-win.spec --onefile --windowed --clean
env/Scripts/pyinstaller.exe smartva-win-cli.spec --onefile --clean

if [[ -f dist/SmartVA.exe && -f dist/SmartVA-cli.exe ]]; then
  exit 0
fi

exit 1
