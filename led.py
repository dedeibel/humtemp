import machine
from time import sleep 

ledpin = machine.Pin(0, machine.Pin.OUT)

def led_on():
    ledpin.value(0)

def led_off():
    ledpin.value(1)

def blink():
    for _ in range(3):
        led_on()
        sleep(0.3)
        led_off()
        sleep(0.3)
