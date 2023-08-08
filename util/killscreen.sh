#!/bin/bash
if ( screen -list | grep -q humtemp ); then
  screen -XS humtemp quit || true
fi
