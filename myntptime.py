import utime
import ntptime

from log import *
from wifi import *

def strftime():
    lt = utime.localtime()
    return "%4d-%02d-%02d %02d:%02d:%02d" % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

# returns the time diff after ntp ran
def init_time_via_ntp():
    log_debug('init time via ntp')
    init_wifi()

    time_before = utime.time()

    ntptime.settime()

    time_diff = utime.time() - time_before
    log_debug('time is: %s (diff after ntp call %d)' % (strftime(), time_diff))
    return time_diff

def unix_time():
    return utime.time() + 946684935; # TODO why the difference to utc?

