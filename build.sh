#!/bin/bash
set -e

if [ ! -e config ]; then
  echo "file 'config'" not found, created one, please fill with values and retry
  cat <<HERE > config
# for the build tool
export CONFIG_SERIAL_DEVICE=/dev/ttyUSB0
export CONFIG_KILL_SCREEN=1
# for the app
export CONFIG_WIFI_ESSID='mywifi'
export CONFIG_WIFI_PASSWD='secret'
export CONFIG_CARBON_HOST='seymourdata'
export CONFIG_CARBON_PORT=2003
# Python: True|False case matters
export CONFIG_DEBUG_LOG_ENABLED=True
HERE
  exit 1
fi


. config

if [ -z "$CONFIG_SERIAL_DEVICE" ]; then
  echo "CONFIG_SERIAL_DEVICE not defined, please check 'config' file"
  exit 1
fi

[ -e dist ] || mkdir dist
rsync --update --delete --recursive --include="*.py" --exclude="*" . dist/
envsubst < main.py > dist/main.py

if [ "$CONFIG_KILL_SCREEN" -eq 1 ]; then
  screen -XS humtemp quit || true
fi

cd dist
for i in `ls -1`; do
  echo "copying $i"
  ampy --port "${CONFIG_SERIAL_DEVICE}" put "$i" "$i"
done

