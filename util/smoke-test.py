import sys
import esp
import machine
from time import sleep 

# copy with
# ampy --port /dev/ttyUSB0 put minimal/minimal-app.py humtemp.py
#
# or
# mpy-cross -O2 -o minimal/humtemp.mpy minimal/minimal-app.py
# ampy --port /dev/ttyUSB0 put minimal/humtemp.mpy humtemp.mpy

def print_mpy_version():
    sys_mpy = sys.implementation._mpy
    arch = [None, 'x86', 'x64',
        'armv6', 'armv6m', 'armv7m', 'armv7em', 'armv7emsp', 'armv7emdp',
        'xtensa', 'xtensawin'][sys_mpy >> 10]
    print('mpy version:', sys_mpy & 0xff)
    print('mpy flags:', end='')
    if arch:
        print(' -march=' + arch, end='')
    if sys_mpy & 0x100:
        print(' -mcache-lookup-bc', end='')
    if not sys_mpy & 0x200:
        print(' -mno-unicode', end='')
    print()

def start():
    print("starting")
    
    fwok = esp.check_fw()
    print("fw ok: "+ str(fwok))
    
    ledpin = machine.Pin(0, machine.Pin.OUT)
    
    def led_on():
        ledpin.value(0)
    
    def led_off():
        ledpin.value(1)
    
    def blink(cycles = 2):
        for i in range(cycles):
            led_on()
            sleep(0.3)
            led_off()
            if i != cycles - 1:
                sleep(0.3)
    
    print("blinking 10")
    blink(10)

    print("blinking 10")
    blink(10)
    
    print("done")

print_mpy_version()
start()
