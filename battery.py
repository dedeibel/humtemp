from machine import ADC
from log import *

adc = None
# As per spec https://docs.micropython.org/en/latest/esp8266/quickref.html#adc-analog-to-digital-conversion
# 0 to value is available
adc_max_val = 1024

# Max seen value empirical using 3xAA
bat_max_expected_voltage = 4.3
# 4.3 devided 47k to 10k, => 0.7543859649
adc_max_val_expected = 772

adc_factor = 1.0 / (adc_max_val + 1)
adc_bat_factor = adc_max_val / adc_max_val_expected
adc_bat_factor_from_read = adc_factor * adc_bat_factor

def init_battery():
    global adc
    adc = ADC(0) # first an only analog pin
    log_debug("battery measuring initialized adc_factor: " + str(adc_factor) + " adc_bat_factor: "+ str(adc_bat_factor))

def read_battery_voltage_raw():
    return adc.read() * adc_factor

def raw_to_battery_percent(raw_voltage):
    return raw_voltage * adc_bat_factor

def raw_to_battery_voltage(raw_voltage):
    return raw_to_battery_percent(raw_voltage) * bat_max_expected_voltage

