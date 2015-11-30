#!/bin/bash

if [[ -f server.pid ]]; then
  kill `cat server.pid`
  if [[ $? -eq 0 ]]; then
    echo OK
    rm server.pid
  fi
fi

