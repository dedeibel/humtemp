#!/bin/bash
set -e
source config
FILE=$1

if [ "${CONFIG_DEBUG_LOG_ENABLED}" == "True" ]; then
  exit 0
fi

echo "- ${FILE}: removing log_debug statements"
# remove log debug statements, except the function definitions
# will only work on single line statements!
perl -i.ori -pe 's/^(?!def )(.*?)log_debug\s*\(.*$/$1pass/' "$FILE" 

echo "- ${FILE}: removing blink_debug statements"
perl -i.ori -pe 's/^(?!def )(.*?)blink_debug\s*\(.*$/$1pass/' "$FILE"

