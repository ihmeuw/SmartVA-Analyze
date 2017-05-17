#!/usr/bin/env bash

set -e

cd ../smartva

find -name "*.pyc" -exec rm {} \;

rm -rf build
rm -rf dist

env/Scripts/pyinstaller.exe smartva-win.spec --onefile --windowed --clean
env/Scripts/pyinstaller.exe smartva-win-cli.spec --onefile --clean

if [[ -f dist/SmartVA-Analyze.exe && -f dist/SmartVA-Analyze-cli.exe ]]; then
  exit 0
fi

exit 1
