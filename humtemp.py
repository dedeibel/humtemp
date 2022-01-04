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
from machine import WDT

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
# main
#

def should_init_time_via_ntp():
    return NTP_UPDATE_TIME == True

def should_send_state_to_carbon():
    return (state_entry_count() % ENTRIES_SEND_BATCH_SIZE) == 0

def should_go_to_deepsleep(iterations):
    return DEEPSLEEP_AFTER_ITERATIONS > 0 and (iterations % DEEPSLEEP_AFTER_ITERATIONS) == 0

def main_loop():
    wdt = WDT()
    wdt.feed()
    iterations = 1
    while True:
        try:
            wdt.feed()

            # Note: Could and probably should be remove in case we send the data
            # directly to the server
            time_diff = None
            if should_init_time_via_ntp():
                time_diff = init_time_via_ntp()

            state_entry = build_state_entry(unix_time(), iterations)
            if time_diff != None:
                set_meta(state_entry, "ntp_diff", time_diff)

            dht22_present = False
            try:
                measure_humidity()
                dht22_present = True
            except Exception as err:
                log_error('Could not measure dht/humidity. Exception: ' + str(err))

            try:
                do_onewire_reading()
            except Exception as err:
                log_error('Could not read onewire data. Exception: ' + str(err))

            wdt.feed()

            # sleeping at least 1 sec since the temp sensor needs time, also humidity
            # sensor can only be read every second
            sleep(1)

            wdt.feed()
            
            if dht22_present:
                try:
                    set_measurement(state_entry, "dht22", "temp", read_humidity_temperature())
                except Exception as err:
                    log_error('Could not read dht/humidity temperature. Exception: ' + str(err))

            try:
                temp_onewire = read_onewire_temp()
                for temp_sensor, value in temp_onewire.items():
                    set_measurement(state_entry, "temp_" + temp_sensor, "temp", value)
            except Exception as err:
                log_error('Could not read onewire temperature. Exception: ' + str(err))

            if dht22_present:
                try:
                    set_measurement(state_entry, "dht22", "humidity", read_humidity())
                except Exception as err:
                    log_error('Could not read dht/humidity humidity. Exception: ' + str(err))

            log_info(state_entry_to_string(state_entry))

            wdt.feed()

            try:
                append_state_entry(state_entry)
            except Exception as err:
                log_error('Error storing measurments locally, ignoring. Exception: ' + str(err))

            if should_send_state_to_carbon():
                try:
                    send_state_to_carbon()
                    truncate_state()
                except Exception as err:
                    log_error('Error sending data, ignoring. Exception: ' + str(err))

            wdt.feed()

            if should_go_to_deepsleep(iterations):
                deepsleep()

            reset_holdoff_timer()

            if SECONDS_BETWEEN_MEASUREMENTS > 0:
                for _ in range(SECONDS_BETWEEN_MEASUREMENTS - 1):
                    wdt.feed()
                    sleep(1)
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
    
    log_debug('init done, starting main loop, carbon prefix: %s' % (CARBON_DATA_PATH_PREFIX))
    main_loop()

