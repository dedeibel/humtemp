#!/bin/bash
set -e

if [ ! -e config ]; then
  echo "file 'config'" not found, created one, please fill with values and retry
  
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

export CONFIG_CARBON_HOST=192.168.0.100
export CONFIG_CARBON_PORT=2003
export CONFIG_CARBON_DATA_PATH_PREFIX=humtemp.office.

# for the ampy client
export AMPY_PORT="\$CONFIG_SERIAL_DEVICE"
export AMPY_BOUD=460800
HERE
  exit 1
fi

echo "reading config file"
. config

if [ -z "$CONFIG_SERIAL_DEVICE" ]; then
  echo "CONFIG_SERIAL_DEVICE not defined, please check 'config' file"
  exit 1
fi

rm -rf dist
mkdir dist

echo "substituting config values"
# substitute config values
for i in `ls -1 *.py`; do
  [[ "$i" =~ ^.*_test.py$ ]] && continue
  [[ "$i" =~ __.py$ ]] && continue

  envsubst < "$i" > dist/"$i"
done

# target dir
cd dist

for i in `ls -1 *.py`; do
  # do nothing to boot.py
  if [[ "$i" == "boot.py" ]]; then
    continue
  fi

  echo "- ${i}: replacing some module imports with upython variants"
  # use upython specific modules, works mostly by changing the import
  # but using the original names allows for local unit testing
  perl -i.ori -pe 's/^from struct /from ustruct /' "$i"

  echo "- ${i}: remove comments"
  # remove comments, save some byte
  #perl -i.ori -pe 's/#.*//' "$i"

  if [ "${CONFIG_DEBUG_LOG_ENABLED}" != "True" ]; then
    echo "- ${i}: removing log_debug statements"
    # remove log debug statements, except the function definitions
    # will only work on single line statements!
    perl -i.ori -pe 's/^(?!def )(.*?)log_debug\s*\(.*$/$1pass/' "$i" 

    echo "- ${i}: removing blink_debug statements"
    perl -i.ori -pe 's/^(?!def )(.*?)blink_debug\s*\(.*$/$1pass/' "$i"
  fi

  # remove empty lines
  echo "- ${i}: remove empty lines"
  perl -i.ori -ne 'print $_ if not s/^\s*\n$//' "$i"

  echo "- ${i}: checking python syntax (py_compile)"
  python3 -m py_compile "$i"
done

echo "include all sub modules in humtemp module"
python3 ../util/includemodules.py humtemp.py humtemp.tmp
mv humtemp.tmp humtemp.py

echo "rechecking python syntax (py_compile)"
python3 -m py_compile humtemp.py
rm -f *.pyc

echo "compile humtemp using mpy-cross"

# Using mpyversion.py:
# mpy version: 5
# mpy flags: -march=xtensa

mpy-cross --version

#
# I did all the "optimization" above before I knew mpy-cross. I had issues with
# not enough storage space or with too little RAM when I used the files as is
# and separated over all those modules. So I removed all the stuff and combined
# it into one. 
# The size still went down even when using mpy-cross and it was easier to keep
# the "one file" solution. So here we are.
#

mpy-cross -march=xtensa -O3 -o humtemp.mpy humtemp.py
# -mcache-lookup-bc gives incompatbile mpy file msg
# -mno-unicode gives incompatbile mpy file msg
# Msg might also be bc of too much memory usage according to
# https://github.com/micropython/micropython/issues/6749

# duck the screen terminal
if [ "$CONFIG_KILL_SCREEN" -eq 1 ]; then
  if ( screen -list | grep -q humtemp ); then
    screen -XS humtemp quit || true
  fi
fi

SIZE=`wc -c humtemp.mpy main.py boot.py | tail -n 1 | awk '{print $1}'`
USED_SIZE=`du --block-size=1 --total humtemp.mpy main.py boot.py | tail --lines 1 | cut --fields 1`

echo "installing to device ${AMPY_PORT} boud ${AMPY_BOUD} real size ${USED_SIZE} (size ${SIZE}) free available 40961"

#echo "NOT SENDING"
#exit

echo "- humtemp.mpy"
ampy put humtemp.mpy
echo "- main.py"
ampy put main.py
echo "- boot.py"
ampy put boot.py
echo "done"
