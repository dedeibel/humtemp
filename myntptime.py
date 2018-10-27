import utime
import ntptime

from log import *
from wifi import init_wifi

def strftime():
    lt = utime.localtime()
    return "%4d-%02d-%02d %02d:%02d:%02d" % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

def init_time_via_ntp():
    log_debug('init time via ntp')
    init_wifi()
    ntptime.settime()
    log_debug('time is: %s' % (strftime()))

def unix_time():
    return utime.time() + 946677735; # TODO why the difference?
