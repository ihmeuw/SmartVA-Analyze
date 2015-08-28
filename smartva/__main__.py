import sys

from smartva import va_ui, va_cli

if __name__ == '__main__':
    if len(sys.argv) > 1:
        va_cli.main()
    else:
        va_ui.main()
