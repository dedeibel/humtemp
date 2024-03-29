import machine
import onewire, ds18x20

from configuration import *
from log import *
from util import *

ds = None
devices = None

def init_temp_sensor():
    global ds
    global devices

    log_debug('initializing temp sensors')

    dat = machine.Pin(TEMP_SENSOR_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))

    try:
        devices = ds.scan()
        i = 0
        for device in devices:
            log_debug('onewire device '+ str(i) +': ' + to_hex_str(device))
            i += 1
    except Exception as err:
        devices = []
        log_error('could not scan onewire devices' + str(err))

    log_debug('init temp sensor done, found onewire devices: '+ str(len(devices)))

def do_onewire_reading():
    global ds
    log_debug('measuring max temp sensor - need to wait 750ms afterwards')
    ds.convert_temp()
    # We need to sleep after issueing the reading.
    # 
    # We'll sleep in the main loop – but don't forget!
    # time.sleep_ms(750)

def read_onewire_temp():
    global ds
    global devices
    log_debug('read onewire temp values')

    temperatures = {}
    for device in devices:
        temperatures[to_hex_str(device)] = ds.read_temp(device)

    return temperatures

