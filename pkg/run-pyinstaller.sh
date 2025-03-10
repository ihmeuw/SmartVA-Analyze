#!/usr/bin/env bash
pyinstaller \
    -p src/ \
    --add-data src/smartva/res:./res \
    --add-data src/smartva/data:./data \
    --icon pkg/icon.png \
    --windowed --onefile --clean \
    --name SmartVA-Analyze \
    app.py
