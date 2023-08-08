#!/bin/bash
set -e
source config

JUSTCOPY="boot.py main.py"
MPY_MODULES=$(for i in dist/*.mpy ; do basename "$i" ; done)

# duck the screen terminal
if [ "$CONFIG_KILL_SCREEN" -eq 1 ]; then
  if ( screen -list | grep -q humtemp ); then
    screen -XS humtemp quit || true
  fi
fi

SIZE=`wc -c ${JUSTCOPY} dist/*.mpy | tail -n 1 | awk '{print $1}'`
USED_SIZE=`du --block-size=1 --total ${JUSTCOPY} dist/*.mpy | tail --lines 1 | cut --fields 1`

echo "installing to device ${AMPY_PORT} boud ${AMPY_BOUD} real size ${USED_SIZE} (size ${SIZE}) free available 40961"

for module in $JUSTCOPY; do
	echo "copying ${module} to device"
	ampy put ${module} ${module} || exit
done
for module in $MPY_MODULES; do
	echo "copying ${module} to device"
	ampy put dist/${module} ${module}|| exit
done 
ampy ls
