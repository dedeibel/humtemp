
# humtemp

Temperature and humidity sensor control for the ESP8266 (HUZZAH ESP8266 breakout)[https://learn.adafruit.com/adafruit-huzzah-esp8266-breakout/overview] in micropython.

 - Measure temperature and humidity
 - Update time and send data to graphite carbon or influx
 - Deepsleep between measurements

## Sensors

 - MAX31820MCR-ND temp sensor https://www.digikey.com/product-detail/en/maxim-integrated/MAX31820MCR/MAX31820MCR-ND/4271348
 - DHT 22 humidity and temp sensor, Adafruit Industries LLC https://www.digikey.com/products/en/sensors-transducers/humidity-moisture-sensors/529?k=dht22

## Wiring Plan

See `./model`.

Notes

 - RHT03 is actually DHT22 (chose the wrong one or was was not available at the
   time)
 - Resistors for ADC circuit are mounted standing up but this does not seem to
   be supported in the breadboard view. So it looks weird.

Default pin assignment:

 - DHT22 on 12
 - Temp Sensor on pin 13

See configuration.py for options.

## Prerequisites

Mostly for the "build" process. Where the script files are stripped down a little.

 - python3
 - python3 venv
 - [requirements.txt](./requirements.txt)
 - perl (for preprocessing, removing debug log statements)
 - mpy_cross
   - https://github.com/micropython/micropython/tree/v1.16/mpy-cross
   - check out or dl https://micropython.org/resources/source/micropython-1.16.tar.xz
   - make, copy to bin
 - micropython v1.20.0 on the esp 

```
source env/bin/activate
pip install -r requirements.txt
```

Copy `mpy_cross` into PATH.

## Flashing esp

 - https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro
 - https://micropython.org/download/esp8266/ e.g. `v1.20.0 (2023-04-26).bin`
 - `esptool.py --port /dev/ttyUSB0 erase_flash`
 - `esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 esp8266-*.bin`

### mpy version

Via: utils/mpyversion.py

Example:

  mpy version: 5
  mpy flags: -march=xtensa

## Building and running

Prepare esp with micropython.

After that:

```
make
```

 - Fill out the created `config` file
 - Connect esp using serial connection (and the configured tty)
 - retry

## Blink Codes

 - 10 times - could not connect to wifi and the network. Going to sleep for a while an retry.
 - 8 times - could not fetch initial ntp time. Going to sleep for a while an retry.
 - 6 times - OSError occured in main loop. Retrying after a few seconds (with increasing holdoff time).
 - 4 times - Exception occured in main loop. Retrying after a few seconds (with increasing holdoff time).

Blinks a lot more when debug is on - so this makes only sense when compiled
without debug.

## Utility Tools

### terminal-loop.sh

Will open a screen session in a loop. It will be closed before flushing
the device and opens up again when using enter.

### util/clean_esp.sh

Removes all files from the esp. 

### util/mpyversion.py

Prints the required mpy version for the installed micropython firmware on the
esp.

### util/smoke-test.py

Call `esp.check_fw()`, and blink the LED.

### util/freespace.sh

Connects to the esp and lists the free flash space.

## References

 - https://learn.adafruit.com/building-and-running-micropython-on-the-esp8266
 - https://docs.micropython.org/en/latest/library/index.html#micropython-specific-libraries
 - https://github.com/micropython/micropython
 - https://github.com/pfalcon/esp-open-sdk

## Improvement Ideas

 - configration.py could be created/filled by the user now that we have multiple modules

