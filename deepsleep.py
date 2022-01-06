import machine

from configuration import *
from log import *
from myntptime import *

rtc = None

def init_deepsleep():
    global rtc

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        log_info('woke from a deep sleep, time is %ds: %s' % (unix_time(), strftime()))
    else:
        log_info('power on or hard reset')
        init_time_via_ntp()

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    log_debug('init deepsleep done')

def deepsleep():
    log_info('going to deepsleep for: %d current time is: %ds: %s' % (DEEPSLEEP_SECONDS * 1000, unix_time(), strftime()))
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, DEEPSLEEP_SECONDS * 1000)
    machine.deepsleep()

