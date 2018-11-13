import machine
import onewire, ds18x20

from configuration import *
from log import *
from util import *

ds = None
roms = None

def init_temp_sensor():
    global ds
    global roms

    dat = machine.Pin(TEMP_SENSOR_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))

    try:
        roms = ds.scan()

        # Ids and positions could be mapped here

        i = 0
        for rom in roms:
            log_debug('onewire rom '+ str(i) +': ' + to_hex_str(rom))
            i += 1
    except Exception as err:
        roms = []
        log_error('could not scan onewire devices' + str(err))

    log_debug('init temp sensor done, found onewire devices: '+ str(len(roms)))

def do_onewire_reading():
    log_debug('measuring max temp sensor')
    ds.convert_temp()
    # we'll sleep in the main loop – but don't forget!
    # time.sleep_ms(750)

def read_onewire_temp():
    log_debug('read onewire temp values')

    # init with 0K :-)
    temperatures = [-273.15, -273.15, -273.15]
    i = 0
    for rom in roms:
        if i >= len(temperatures):
            break
        temperatures[i] = ds.read_temp(rom)
        i += 1

    return temperatures

def read_onewire_temp_from_first_device():
    log_debug('read onewire temp value of first device')

    temp = 0
    for rom in roms:
        temp = ds.read_temp(rom)
        break
    return temp

