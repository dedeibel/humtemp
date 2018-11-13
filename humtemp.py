from time import sleep

from configuration import *
from log import *
from led import *
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

def print_results(temp_dht, humidity, temp_onewire):
    log_info('temp_dht: {:.1f} *C\ntemp1: {:.1f} *C\ntemp2: {:.1f} *C\ntemp3: {:.1f} *C\nhumidity: {}%'.format(
        temp_dht, temp_onewire[0], temp_onewire[1], temp_onewire[2], humidity))

#
# main
#

def should_delete_old_entries():
    # TODO file db size close to 4k
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
            if should_delete_old_entries():
                delete_older_state_entries()

            if should_init_time_via_ntp():
                init_time_via_ntp()

            measure_humidity()

            do_onewire_reading()
            # sleeping at least 1 sec since the temp sensor needs time, also humidity
            # sensor can only be read every second
            sleep(1)

            temp_dht = read_humidity_temperature()
            temp_onewire = read_onewire_temp()
            humidity = read_humidity()
            print_results(temp_dht, humidity, temp_onewire)

            try:
                state_entry = build_state_entry(
                        unix_time(),
                        iterations,
                        temp_dht,
                        humidity,
                        temp_onewire[0],
                        temp_onewire[1],
                        temp_onewire[2])
                append_state_entry(state_entry)
            except Exception as err:
                log_error('Error storing measurments locally, ignoring. Exception: ' + str(err))

            if should_send_state_to_carbon():
                try:
                    send_state_to_carbon()
                    truncate_state()
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

def start():
    init_deepsleep()
    init_temp_sensor()
    init_humid_sensor()
    init_state()
    reset_holdoff_timer()
    blink()
    
    log_debug('init done, starting main loop')
    main_loop()

