#!/bin/bash
set -e

cd ~/build-agent/smartva

git fetch
git checkout $1
git pull

# env/Scripts/pip install -r requirements-win.txt

