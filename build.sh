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
  # use upython specific modules
  perl -pe 's/^from struct /from ustruct /' "$i" > "$i".tmp
  mv "$i".tmp "$i"

  # remove comments
  perl -pe 's/#.*//' "$i" > "$i".tmp
  mv "$i".tmp "$i"

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

SIZE=`du --block-size=1 --total humtemp.mpy main.py boot.py | tail --lines 1 | cut --fields 1`
echo "installing to device ${AMPY_PORT} boud ${AMPY_BOUD} size $SIZE (available 40961)"

ampy put humtemp.mpy
ampy put main.py
ampy put boot.py
