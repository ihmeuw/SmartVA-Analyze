Windows development and build instructions:
https://hub.ihme.washington.edu/display/IIW/SmartVA+Windows+Development+Instructions

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

