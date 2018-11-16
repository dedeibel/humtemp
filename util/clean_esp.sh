#!/bin/bash
set -e
PORT=/dev/ttyUSB0
for i in `ampy --port ${PORT} ls`; do
  echo "ampy rm $i"
  ampy --port ${PORT} rm "$i"
done
