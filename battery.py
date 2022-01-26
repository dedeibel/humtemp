from machine import ADC
from log import *

adc = None
# As per spec https://docs.micropython.org/en/latest/esp8266/quickref.html#adc-analog-to-digital-conversion

# 1 MOhm vs 220 kOhm voltage divider
# battery_factor = 0.18033
# 1 / battery_factor
battery_factor_one_over = 5.545454

# 47 kOhm vs 10 kOhm voltage divider
# battery_factor = 0.17544
# 1 / battery_factor
# battery_factor_one_over = 5.7

# adc_max_val = const(1023)
# 1 / adc_max_val
# (zero is also available)
# times 1000 for mV
adc_factor = 0.9775
# by experiment, thousands
adc_offset_mv = 0

# adc_min_working_val = 0.65 # by experiment

def init_battery():
    global adc
    adc = ADC(0) # first an only analog pin
    log_debug("battery measuring initialized adc_factor: " + str(adc_factor) + " battery_factor_one_over: "+ str(battery_factor_one_over))

# in mV
def read_voltage_raw():
    return adc.read() * adc_factor + adc_offset_mv

# in mV
def raw_to_battery_voltage(raw_voltage):
    return raw_voltage * battery_factor_one_over

