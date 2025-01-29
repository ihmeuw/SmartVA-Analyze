import os
import signal
import time
import threading

import http.server
import http.server

watched_files = ['SmartVA-Analyze.exe'.lower()]
start = time.time()
run_time = 60


class SimpleHTTPRequestHandlerFileWatcher(http.server.SimpleHTTPRequestHandler):
    def copyfile(self, source, outputfile):
        if isinstance(source, file):
            filename = os.path.split(source.name)[-1]
            if filename.lower() in watched_files:
                watched_files.remove(filename.lower())
        http.server.SimpleHTTPRequestHandler.copyfile(self, source, outputfile)


httpd = http.server.HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandlerFileWatcher)
print(('{address[0]}:{address[1]} - - Listening...'.format(address=httpd.server_address)))

t = threading.Thread(target=httpd.serve_forever)
t.daemon = True
t.start()


def shutdown(signum=None, frame=None):
    success = not len(watched_files)
    print(('{address[0]}:{address[1]} - - Shutting down.'.format(address=httpd.server_address)))
    exit(int(not success))


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

while True:
    time.sleep(1)

