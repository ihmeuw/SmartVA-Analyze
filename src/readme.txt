To bundle the source as a single binary, run the following commands with PyInstaller 2.1

# On Mac OS X
pyinstaller pkg/smartva-mac.spec --onefile --windowed

# On Windows
pyinstaller pkg/smartva-win.spec --onefile --windowed

# Notes
The spec files disable UPX because it doesn't work with 64-bit Python on OS X (10.6+).
The spec files disable console mode because we print logging information to the UI.
The Windows spec file has code to remove duplication of pyconfig.h in the Windows build.
If you add new files to the source, be sure to add any non-Python files (e.g., CSV) to the *.spec files.
