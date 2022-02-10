from machine import Pin
from time import sleep_ms

BLINK_MS = 400
# start off initially
ledpin = Pin(0, Pin.OUT, value=1)

def led_on():
    ledpin.value(0)

def led_off():
    ledpin.value(1)

def blink_debug(cycles = 1):
    blink(cycles)

def blink(cycles = 1, overal_duration_ms = BLINK_MS):
    led_off()
    pause_ms = int(overal_duration_ms / cycles)
    for i in range(cycles):
        led_on()
        sleep_ms(pause_ms)
        led_off()
        if i != cycles - 1:
            sleep_ms(pause_ms)

