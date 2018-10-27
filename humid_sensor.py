import machine
import dht

from configuration import *
from log import *

dht22 = None

def init_humid_sensor():
    global dht22
    dht22 = dht.DHT22(machine.Pin(DHT22_PIN))

def measure_humidity():
    log_debug('measuring dht22')
    dht22.measure()

def read_humidity_temperature():
    log_debug('read dht22 temp value')
    return dht22.temperature()

def read_humidity():
    log_debug('read dht22 humidity value')
    return dht22.humidity()
