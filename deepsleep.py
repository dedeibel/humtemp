import machine

from configuration import *
from log import *
from myntptime import *

rtc = None

def init_deepsleep():
    global rtc

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        log_debug('woke from a deep sleep, time is %ds: %s' % (unix_time(), strftime()))
    else:
        log_debug('power on or hard reset')
        init_time_via_ntp()

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    log_debug('init deepsleep done')

# use https://docs.micropython.org/en/latest/library/esp.html?highlight=deepsleep#esp.deepsleep
# or https://docs.micropython.org/en/latest/library/machine.html#machine.deepsleep

def deepsleep():
    if DEBUG_LOG_ENABLED:
        log_debug('going to deepsleep for: %d current time is: %ds: %s' % (DEEPSLEEP_MS, unix_time(), strftime()))
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, DEEPSLEEP_MS)
    # doc seems outdated about esp.deepsleep - it does nothing, use
    # machine.deepsleep
    machine.deepsleep(DEEPSLEEP_MS)

