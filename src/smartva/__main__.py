import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        from smartva import va_cli as app
    else:
        from smartva import va_ui as app
    app.main()
