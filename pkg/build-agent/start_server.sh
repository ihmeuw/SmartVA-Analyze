#!/usr/bin/env bash

set -e

./kill_server.sh

nohup python ~/build-agent/file_server.py >server.log 2>&1&
echo $! > server.pid
