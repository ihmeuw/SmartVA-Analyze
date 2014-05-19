To bundle the source as a single binary, run the following commands with PyInstaller 2.1

First edit the appropriate smartva-[platform].spec file and replace the paths with the appropriate local paths on your machine.

for mac replace:
/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/

for windows replace:
Z:\\

and add the whole path to the first line with src/vaUI.py
and the last line with the icon

# On Mac OS X
python pyinstaller.py pkg/smartva-mac.spec --onefile --windowed

C:\Documents and Settings\Administrator\Desktop\PyInstaller-2.1>python pyinstall
er.py "c:\Documents and Settings\Administrator\Desktop\ihme-va\pkg\smartva-win.s
pec" --onefile --windowed

# On Windows
python pyinstaller.py pkg\smartva-win.spec --onefile --windowed

# Notes
The spec files disable UPX because it doesn't work with 64-bit Python on OS X (10.6+).
The spec files disable console mode because we print logging information to the UI.
The Windows spec file has code to remove duplication of pyconfig.h in the Windows build.
If you add new files to the source, be sure to add any non-Python files (e.g., CSV) to the *.spec files.


To build the installer use:
BitRock InstallBuilder Professional 8.6.0

choose ‘open’ and open the smartva.xml located in the ihme/pkg directory
under ‘files’ on the left edit the ‘Program Files’ to be the appropriate local paths

The license file is license.xml included in the ihme/pkg directory

the installer will be in ‘output’ directory wherever BitRock InstallerBuilder was installed.

