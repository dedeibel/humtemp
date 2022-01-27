from configuration import *
from machine import ADC
from log import *

adc = None

def init_battery():
    global adc
    adc = ADC(0) # first an only analog pin
    log_debug("battery measuring initialized adc_factor: " + str(ADC_FACTOR_ONE_OVER) + " battery_factor_one_over: "+ str(BATTERY_FACTOR_ONE_OVER))

# in mV
def read_voltage_raw():
    return adc.read() * ADC_FACTOR_ONE_OVER + ADC_OFFSET_MV

# in mV
def raw_to_battery_voltage(raw_voltage):
    return raw_voltage * BATTERY_FACTOR_ONE_OVER

