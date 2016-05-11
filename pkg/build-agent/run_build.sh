#!/bin/bash

cd smartva

rm -rf build
rm -rf dist
find ./smartva -name "*.pyc" -exec rm {} \;

env/Scripts/pyinstaller.exe pkg/smartva-win.spec --onefile --clean



if [[ -f dist/SmartVA.exe ]]; then
  exit 0
fi

exit 1

