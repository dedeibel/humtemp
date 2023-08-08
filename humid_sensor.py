import machine
import dht

from configuration import *
from log import *

mydht22 = None

def init_humid_sensor():
    global mydht22

    log_debug('initializing dht22')
    mydht22 = dht.DHT22(machine.Pin(DHT22_PIN))

def measure_humidity():
    global mydht22
    log_debug('measuring dht22')
    mydht22.measure()

def read_humidity_temperature():
    global mydht22
    log_debug('read dht22 temp value')
    return mydht22.temperature()

def read_humidity():
    global mydht22
    log_debug('read dht22 humidity value')
    return mydht22.humidity()
