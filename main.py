from time import sleep

from configuration import *
from log import *
from myntptime import *
from deepsleep import *
from temp_sensor import *
from humid_sensor import *
from state import *
from carbon import *

from linestore import *

#
# error handling
#

def reset_holdoff_timer():
    global last_err_timeout_seconds
    last_err_timeout_seconds = 1

def next_holdoff_seconds():
    global last_err_timeout_seconds
    if last_err_timeout_seconds > ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS:
        return ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS
    else:
        last_err_timeout_seconds *= 2
        return last_err_timeout_seconds

#
# utility
#

def print_results(temp_dht, temp_maxin, humidity):
    log_info('temp_dht: {:.1f} *C \t temp_maxin: {:.1f} *C \t humidity: {}%'.format(
        temp_dht, temp_maxin, humidity))

#
# main
#

def should_delete_older_entries():
    return state_entry_count() >= STATE_MAX_ENTRIES

def should_init_time_via_ntp():
    return state_entry_count() % NTP_REFRESH_EACH_N_ITERATIONS == 0

def should_send_state_to_carbon():
    return state_entry_count() % ENTRIES_SEND_BATCH_SIZE == 0 or state_entry_count() >= STATE_MAX_ENTRIES

def should_go_to_deepsleep():
    return state_entry_count() % ENTRIES_MEASURE_BATCH_SIZE == 0

def main_loop():
    iterations = 1
    while True:
        try:
            if should_delete_older_entries():
                delete_older_state_entries()

            if should_init_time_via_ntp():
                init_time_via_ntp()

            measure_humidity()

            do_onewire_reading()
            # sleeping at least 1 sec since the temp sensor needs time, also humidity sensor can only be
            # read every second
            sleep(1)

            temp_dht = read_humidity_temperature()
            temp_maxin = read_onewire_temp_from_first_device()
            humidity = read_humidity()
            print_results(temp_dht, temp_maxin, humidity)

            try:
                state_entry = build_state_entry(unix_time(), iterations, temp_dht, temp_maxin, humidity)
                append_state_entry(state_entry)
                store_state()
            except Exception as err:
                log_error('Error storing measurments locally, ignoring. Exception: ' + str(err))

            if should_send_state_to_carbon():
                try:
                    send_state_to_carbon()
                    delete_state_entries()
                    store_state()
                except Exception as err:
                    log_error('Error sending data, ignoring. Exception: ' + str(err))

            if should_go_to_deepsleep():
                deepsleep()

            reset_holdoff_timer()

            sleep(SECONDS_BETWEEN_MEASUREMENTS)
        except Exception as err:
            timeout_seconds = next_holdoff_seconds()
            log_error('Error in mainloop! (sleeping for %d seconds): %s' % (timeout_seconds, str(err)))
            # Errno 110 ETIMEOUT might be a sensor is not available or responding, check cables
            sleep(timeout_seconds)
        finally:
            iterations += 1

init_deepsleep()
init_temp_sensor()
init_humid_sensor()
init_state()
reset_holdoff_timer()
blink()
log_debug('x init done, starting main loop')

log_debug('XXXX init linestore')
store = Linestore(path)
store.open()
store.append(1, [2.0])
store.close()
store.open()
result = store.readlines(2)
log_debug('XXXX')
log_debug('result:' + str(result))
log_debug('XXXX')

main_loop()

