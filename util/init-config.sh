#!/bin/bash
set -e

if [ -e config ]; then
  echo "config already existing, exiting"
  # okay, build can continue
  exit 0
fi

echo "file 'config' not found, I created one, please adapt and retry build"
  
# default config values
cat <<HERE > config
# Also used to remove log statements during preprocessing. Python True/False.
export CONFIG_DEBUG_LOG_ENABLED=True

export CONFIG_SERIAL_DEVICE=/dev/ttyUSB0

# Kills screen to allow flashing, see terminal-loop.sh
export CONFIG_KILL_SCREEN=0

export CONFIG_WIFI_ESSID='mywifi'
export CONFIG_WIFI_PASSWD='secure'
export CONFIG_WIFI_USE_STATIC_IP=True
export CONFIG_WIFI_IP=192.168.0.10
export CONFIG_WIFI_NETMASK=255.255.255.0
export CONFIG_WIFI_GATEWAY=192.168.0.1
export CONFIG_WIFI_DNS_SERVER=192.168.0.1

export CONFIG_NTP_HOST=pool.ntp.org

export CONFIG_CARBON_HOST=192.168.0.100
export CONFIG_CARBON_PORT=2003
export CONFIG_CARBON_DATA_PATH_PREFIX=humtemp.office.

# for the ampy client
export AMPY_PORT="\$CONFIG_SERIAL_DEVICE"
export AMPY_BOUD=460800
HERE

# error because we want the build to fail once
exit -1
