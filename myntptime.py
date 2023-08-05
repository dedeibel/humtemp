import utime
import ntptime
import errno

from log import *
from wifi import *

time_diff = None

# might be None
def get_ntp_time_diff():
    return time_diff

def strftime():
    lt = utime.localtime()
    return "%4d-%02d-%02d %02d:%02d:%02d" % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

# returns the time diff after ntp ran or None if it did not update via ntp
def init_time_via_ntp():
    log_debug('init time via ntp')
 
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        log_debug('woke from a deep sleep, time is %ds: %s' % (unix_time(), strftime()))
        if NTP_SKIP_AFTER_DEEPSLEEP:
            log_debug('not fetching ntp time')
            return None
    else:
        log_debug('power on or hard reset')

    ntptime.host = NTP_HOST

    # Can fail with OSError, so allow for a retry
    for _ in range(5): 
        try:
            time_before = utime.time()

            ntptime.settime()

            global time_diff
            time_diff = utime.time() - time_before
            log_debug('time is: %s (diff after ntp call %d)' % (strftime(), time_diff))

            return time_diff
        except OSError as err:
            exerrno = err.errno
            errnomsg = errno.errorcode[exerrno]
            log_error('Error fetching ntp time! errno: %d errnomsg: %s excpt: %s' % (exerrno, errnomsg, str(err)))
            sleep(1)
    raise Exception("Could not init time via ntp")

def unix_time():
    return utime.time() + 946684935; # TODO why the difference to utc?

