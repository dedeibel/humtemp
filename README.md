
# humtemp

work in progress

Temperature and humidity sensor control for the ESP8266 (HUZZAH ESP8266 breakout) in micropython.

 - Measure and store data in batches
 - Deepsleep between batches
 - Update time and send data to graphite carbon after a couple of batches

## Sensors

 - MAX31820MCR-ND temp sensor https://www.digikey.com/product-detail/en/maxim-integrated/MAX31820MCR/MAX31820MCR-ND/4271348
 - DHT 22 humidity and temp sensor, Adafruit Industries LLC https://www.digikey.com/products/en/sensors-transducers/humidity-moisture-sensors/529?k=dht22

## Wiring Plan

_TODO_

Default pins

 - DHT22 on 12
 - Temp Sensor on pin 13

See configuration.py for options.

## Prerequisites

 - python
 - adafruit `ampy` (`pip install ampy`)
 - `mpy_cross` https://github.com/micropython/micropython/tree/master/mpy-cross
 - micropython on the esp 

## Building and running

Prepare esp with micropython.

```
./build.sh
```

 - Fill out the created `config` file
 - Connect esp using serial connection (and the configured device)

```
./build.sh
```

Or manually call `envsubst` from the build script and then copy the files to your micropython
prepared esp.

## Util Tools

### includemodules.py

Works only for module files that are present in the current directory. Works
only for imports of all symbols.

```
pip install pathlib
```

## References

 - https://learn.adafruit.com/building-and-running-micropython-on-the-esp8266
 - https://docs.micropython.org/en/latest/library/index.html#micropython-specific-libraries
 - https://github.com/micropython/micropython
 - https://github.com/pfalcon/esp-open-sdk

## TODOs

 - Test deepsleep accuracy
 - Determine how much entries could be stored max
 - Determine how much entries to store

## Improvement Ideas

 - Do not even build output strings if debug is off
 - Use are more robust storage format than json, maybe line based with some sansity checks. In case of a broken file only affected entries should be lost.

