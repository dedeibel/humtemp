import machine
import onewire, ds18x20

from configuration import *
from log import *

ds = None
roms = None

def init_temp_sensor():
    global ds
    global roms

    dat = machine.Pin(TEMP_SENSOR_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    roms = ds.scan()
    log_debug('init temp sensor done, found onewire devices: ' + str(roms))

def do_onewire_reading():
    log_debug('measuring max temp sensor')
    ds.convert_temp()
    # we sleep anyway for beeping in the main loop
    # time.sleep_ms(750)

def read_onewire_temp_from_first_device():
    log_debug('read onewire temp value')

    temp = 0
    for rom in roms:
        temp = ds.read_temp(rom)
        break
    return temp

