#!/bin/bash

if [ ! -e config ]; then
  echo "file 'config'" not found, created one, please fill with values and retry
  cat <<HERE > config
export CONFIG_WIFI_ESSID='mywifi'
export CONFIG_WIFI_PASSWD='secret'
export CONFIG_CARBON_HOST='seymourdata'
export CONFIG_CARBON_PORT=2003
HERE
  exit 1
fi

. config
envsubst < main.py
