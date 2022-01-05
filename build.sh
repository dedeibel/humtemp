#!/bin/bash
set -e

if [ ! -e config ]; then
  echo "file 'config'" not found, created one, please fill with values and retry
  
  # default config values
  cat <<HERE > config
# for the build tool
export CONFIG_SERIAL_DEVICE=/dev/ttyUSB0
export CONFIG_KILL_SCREEN=0
# for the app
export CONFIG_WIFI_ESSID='mywifi'
export CONFIG_WIFI_PASSWD='secret'
export CONFIG_CARBON_HOST='seymourdata'
export CONFIG_CARBON_PORT=2003
# Python: True|False case matters
export CONFIG_DEBUG_LOG_ENABLED=True
export CARBON_DATA_PATH_PREFIX="humtemp."

# for the ampy client
export AMPY_PORT=\$CONFIG_SERIAL_DEVICE
export AMPY_BOUD=460800
HERE
  exit 1
fi

. config

if [ -z "$CONFIG_SERIAL_DEVICE" ]; then
  echo "CONFIG_SERIAL_DEVICE not defined, please check 'config' file"
  exit 1
fi

[ -e dist ] || mkdir dist

# substitute config values
for i in `ls -1 *.py`; do
  [[ "$i" =~ ^.*_test.py$ ]] && continue
  [[ "$i" =~ __.py$ ]] && continue

  envsubst < "$i" > dist/"$i"
done

# target dir
cd dist

for i in `ls -1 *.py`; do
  if [[ "$i" == "boot.py" ]]; then
    continue
  fi

  # use upython specific modules, works mostly by changing the import
  # but using the original names allows for local unit testing
  perl -pe 's/^from struct /from ustruct /' "$i" > "$i".tmp
  mv "$i".tmp "$i"

  # remove comments, save some byte
  perl -pe 's/#.*//' "$i" > "$i".tmp
  mv "$i".tmp "$i"

  if [ "${CONFIG_DEBUG_LOG_ENABLED}" != "True" ]; then
    # remove log debug statements, except the function definitions
    perl -pe 's/(?!def )\s*log_debug\s*\((\([^\)]*\)|[^\(\)]*)\)\s*(?!:)\s*//' "$i" > "$i".tmp
    mv "$i".tmp "$i"

    perl -pe 's/(?!def )\s*blink_debug\s*\((\([^\)]*\)|[^\(\)]*)\)\s*(?!:)\s*//' "$i" > "$i".tmp
    mv "$i".tmp "$i"
  fi

  # remove empty lines
  perl -ne 'print $_ if not s/^\s*\n$//' "$i" > "$i".tmp
  mv "$i".tmp "$i"

  # syntax check
  python3 -m py_compile "$i"
done

python3 ../util/includemodules.py humtemp.py humtemp.tmp
mv humtemp.tmp humtemp.py

python3 -m py_compile humtemp.py
rm -f *.pyc

#  -mcache-lookup-bc gives incompatbile mpy file msg
mpy-cross -O2 -o humtemp.mpy humtemp.py

# duck the screen terminal
if [ "$CONFIG_KILL_SCREEN" -eq 1 ]; then
  if ( screen -list | grep -q humtemp ); then
    screen -XS humtemp quit || true
  fi
fi

SIZE=`wc -c humtemp.mpy main.py boot.py | tail -n 1 | awk '{print $1}'`
USED_SIZE=`du --block-size=1 --total humtemp.mpy main.py boot.py | tail --lines 1 | cut --fields 1`
echo "installing to device ${AMPY_PORT} boud ${AMPY_BOUD} real size ${USED_SIZE} (size ${SIZE}) free available 40961"

ampy put humtemp.mpy
ampy put main.py
ampy put boot.py
