import errno
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
from battery import *

#
# error handling
#

last_err_timeout_seconds = 1

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
    # Temporarily: for measuring if setting ntp time after each deep sleep is required
    time_diff = None
    if should_init_time_via_ntp():
        time_diff = init_time_via_ntp()

    error_count = 0
    iterations = 1
    while True:
        try:
            blink_debug(3)
            state_entry = build_state_entry(unix_time(), iterations)
            # Temporarily: for measuring if setting ntp time after each deep sleep is required
            if time_diff != None:
                set_meta(state_entry, "ntp_diff", time_diff)

            dht22_present = False
            try:
                measure_humidity()
                dht22_present = True
            except Exception as err:
                error_count += 1
                log_error('Could not measure dht/humidity. Exception: ' + str(err))

            blink_debug()

            try:
                do_onewire_reading()
            except Exception as err:
                error_count += 1
                log_error('Could not read onewire data. Exception: ' + str(err))

            blink_debug()
            log_debug('sleeping to allow sensors to init')

            # sleeping at least 1 sec since the temp sensor needs time, also humidity
            # sensor can only be read every second
            sleep(1)

            if dht22_present:
                try:
                    set_measurement(state_entry, "dht22", "temp", read_humidity_temperature())
                except Exception as err:
                    error_count += 1
                    log_error('Could not read dht/humidity temperature. Exception: ' + str(err))

            try:
                temp_onewire = read_onewire_temp()
                for temp_sensor, value in temp_onewire.items():
                    set_measurement(state_entry, "temp_" + temp_sensor, "temp", value)
            except Exception as err:
                error_count += 1
                log_error('Could not read onewire temperature. Exception: ' + str(err))

            if dht22_present:
                try:
                    set_measurement(state_entry, "dht22", "humidity", read_humidity())
                except Exception as err:
                    error_count += 1
                    log_error('Could not read dht/humidity humidity. Exception: ' + str(err))

            log_debug('finished measurements')

            if READ_BATTERY_FROM_ADC:
                try:
                    log_debug('reading battery voltage')
                    adc_voltage_raw = read_voltage_raw()
                    battery_voltage = raw_to_battery_voltage(adc_voltage_raw)
                    log_debug('adc voltage raw: ' + str(adc_voltage_raw) + ' battery voltage: '+ str(battery_voltage));
                    blink_debug()
                    set_measurement(state_entry, "adc0", "voltage", adc_voltage_raw)
                    set_measurement(state_entry, "battery", "voltage", battery_voltage)
                except Exception as err:
                    error_count += 1
                    log_error('Could not read battery voltage. Exception: ' + str(err))

            set_meta(state_entry, "error_count", error_count)
            error_count = 0

            if DEBUG_LOG_ENABLED:
                log(state_entry_to_string(state_entry))

            try:
                append_state_entry(state_entry)
            except Exception as err:
                error_count += 1
                log_error('Error storing measurments locally, ignoring. Exception: ' + str(err))

            blink_debug()

            if should_send_state_to_carbon():
                try:
                    blink_debug(state_entry_count())
                    send_state_to_carbon()
                    truncate_state()
                except Exception as err:
                    # error_count is sent at this point - but keep counting in
                    # case of multiple iteration it will show up
                    error_count += 1
                    log_error('Error sending data, ignoring. Exception: ' + str(err))

            blink_debug()

            if should_go_to_deepsleep(iterations):
                blink_debug(6)
                wifi_disconnect()
                deepsleep()

            reset_holdoff_timer()

            if SECONDS_BETWEEN_MEASUREMENTS > 0:
                log_debug('sleeping between measurements for seconds: ' + str(SECONDS_BETWEEN_MEASUREMENTS))
                for _ in range(SECONDS_BETWEEN_MEASUREMENTS - 1):
                    sleep(1)
        except OSError as err:
            error_count += 1
            exerrno = err.errno
            errnomsg = errno.errorcode[exerrno]
            timeout_seconds = next_holdoff_seconds()
            log_error('Error in mainloop! (sleeping for %d seconds) errno: %d errnomsg: %s excpt: %s' % (timeout_seconds, exerrno, errnomsg, str(err)))
            sleep(timeout_seconds)
        except Exception as err:
            error_count += 1
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
    if READ_BATTERY_FROM_ADC:
        init_battery()
    reset_holdoff_timer()
    blink_debug()
    
    log_debug('init done, starting main loop, carbon prefix: %s' % (CARBON_DATA_PATH_PREFIX))
    main_loop()

