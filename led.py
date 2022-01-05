import machine
from time import sleep 

BLINK_SECONDS = 0.4
ledpin = machine.Pin(0, machine.Pin.OUT)

def led_on():
    ledpin.value(0)

def led_off():
    ledpin.value(1)

def blink_debug(cycles = 1):
    blink(cycles)

def blink(cycles = 1):
    pause_seconds = BLINK_SECONDS / cycles
    for i in range(cycles):
        led_on()
        sleep(pause_seconds)
        led_off()
        if i != cycles - 1:
            sleep(pause_seconds)

