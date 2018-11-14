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

  perl -pe 's/#.*//' dist/"$i" > dist/"$i".tmp
  mv dist/"$i".tmp dist/"$i"

  perl -ne 'print $_ if not s/^\s*\n$//' dist/"$i" > dist/"$i".tmp
  mv dist/"$i".tmp dist/"$i"
done

# duck the screen terminal
if [ "$CONFIG_KILL_SCREEN" -eq 1 ]; then
  screen -XS humtemp quit || true
fi

# target dir
cd dist

# syntax check
for i in `ls -1 *.py`; do
  python -m py_compile "$i"
done
rm -f *.pyc

python ../util/includemodules.py main.py main.tmp
mv main.tmp main.py

python -m py_compile main.py
rm -f *.pyc

#ampy --port "${CONFIG_SERIAL_DEVICE}" put boot.py
#ampy --port "${CONFIG_SERIAL_DEVICE}" put main.py

#SIZE=`du --block-size=1 --total *py | tail --lines 1 | cut --fields 1`
#echo "size $SIZE (available 40960)"
#
## copy to device
#for i in `ls -1 *.py`; do
#  echo "copying $i"
##  ampy --port "${CONFIG_SERIAL_DEVICE}" put "$i" "$i"
#done

