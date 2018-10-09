from time import sleep
import utime
import network
import socket
import sys

import ntptime
import ujson
import machine
import dht
import onewire, ds18x20

WIFI_ESSID = '$CONFIG_WIFI_ESSID'
WIFI_PASSWD = '$CONFIG_WIFI_PASSWD'
CARBON_HOST = '$CONFIG_CARBON_HOST'
CARBON_PORT = $CONFIG_CARBON_PORT

DEBUG_LOG_ENABLED = $CONFIG_DEBUG_LOG_ENABLED


DHT22_PIN = 12
TEMP_SENSOR_PIN = 13
# about 3:30h max https://thingpulse.com/max-deep-sleep-for-esp8266/
DEEPSLEEP_MS = 30 * 1000
STORAGE_FILENAME = 'db.dat'

ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS = 60

dht22 = dht.DHT22(machine.Pin(DHT22_PIN))
ledpin = machine.Pin(0, machine.Pin.OUT)

rtc = None
ds = None
roms = None
carbon_addr = None
state = None
now = None

#
# temp sensor
#

def init_temp_sensor():
    global ds
    global roms

    dat = machine.Pin(TEMP_SENSOR_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    roms = ds.scan()
    log_debug('init temp sensor done, found onewire devices: ' + str(roms))

def do_onewire_reading():
    ds.convert_temp()
    # we sleep anyway for beeping in the main loop
    # time.sleep_ms(750)

def read_onewire_temp_from_first_device():
    temp = 0
    for rom in roms:
        temp = ds.read_temp(rom)
        break
    return temp

#
# wifi and network
#

def init_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log_debug('connecting to network '+ WIFI_ESSID + ' ...')
        sta_if.active(True)
        sta_if.connect(WIFI_ESSID, WIFI_PASSWD)
        while not sta_if.isconnected():
            sleep(.3)
            log_debug('waiting ...')
            pass
    log_debug('init wifi done, network config: ' + str(sta_if.ifconfig()))

def init_addr_info():
    global carbon_addr

    carbon_addr_info = socket.getaddrinfo(CARBON_HOST, CARBON_PORT)
    # OS Error 2 here means host not found / resolvable

    # TODO can be temporary, reboot / join the error loop
    carbon_addr = carbon_addr_info[0][-1]
    log_debug('init addr info done, sending data to ' + CARBON_HOST + ':' + str(CARBON_PORT))

def send_to_carbon(temp_a, temp_b, humidity):
    s = socket.socket()
    s.connect(carbon_addr)
    s.send('test.heidestock.temp.a %.2f -1\n' % (temp_a))
    s.send('test.heidestock.temp.b %.2f -1\n' % (temp_b))
    s.send('test.heidestock.humidity %.2f -1\n' % (humidity))
    s.close()


#
# power management
#

def init_deepsleep():
    global rtc

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        log_debug('woke from a deep sleep')
    else:
        log_debug('power on or hard reset')

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    log_debug('init deepsleep done')

def deepsleep():
    log_debug('going to deepsleep for: '+ str(DEEPSLEEP_MS))
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, DEEPSLEEP_MS)
    machine.deepsleep()


#
# led control
#

def led_on():
    ledpin.value(0)

def led_off():
    ledpin.value(1)

def blink():
    for _ in range(3):
        led_on()
        sleep(0.3)
        led_off()
        sleep(0.3)

#
# time
#

def init_time_via_ntp():
    global now
    ntptime.settime()
    now = utime.time()

#
# state and state storage
#

def build_state_entry(time, iterations, temp_dht, temp_maxin, humidity):
    return {'time': time, 'iterations': iterations, 'temp_dht': temp_dht, 'temp_maxin': temp_maxin, 'humidity': humidity}

def append_state_entry(state_entry):
    global state
    state.append(state_entry)

def state_entry_count():
    global state
    return len(state)

def init_state():
    touch_file(STORAGE_FILENAME)
    load_state()

def touch_file(file_path):
    db_file = open(file_path, 'a')
    db_file.close()

def load_state():
    log_debug('loading db state')
    global state
    state = do_load_state()

def do_load_state():
    db_file = open(STORAGE_FILENAME, 'r+')
    try:
        the_read_state = ujson.load(db_file)
        if the_read_state != None:
            return the_read_state
    except ValueError as ve:
        # might happen initially, start with empty state
        log_debug('could not read state file, starting fresh')
    finally:
        db_file.close()

    return []

def store_state():
    global state
    log_debug('storing db state')
    db_file = open(STORAGE_FILENAME, 'w+')
    try:
        ujson.dump(state, db_file)
    finally:
        db_file.close()

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
    log_info("temp_dht: {:.1f} *C \t temp_maxin: {:.1f} *C \t humidity: {}%".format(
        temp_dht, temp_maxin, humidity))

# does not obey log setting
def print_state():
    global state
    print("state")
    print(ujson.dumps(state))

def log_debug(message):
    if DEBUG_LOG_ENABLED:
        print(message)

def log_info(message):
    print(message)

def log_error(message):
    print(message)

#
# main
#

def main_loop():
    iterations = 1
    while True:
        try:
            log_debug("measuring dht22")
            dht22.measure()
            led_on()

            log_debug("measuring max temp sensor")
            do_onewire_reading()
            led_off()
            # sleeping at least 1 sec
            sleep(1)

            log_debug("read dht22 value")
            temp_dht = dht22.temperature()

            log_debug("read max temp value")
            temp_maxin = read_onewire_temp_from_first_device()

            humidity = dht22.humidity()

            print_results(temp_dht, temp_maxin, humidity)

            try:
                state_entry = build_state_entry(now, iterations, temp_dht, temp_maxin, humidity)
                append_state_entry(state_entry)
                log_debug("storing current state, with "+ str(state_entry_count()) +" entries")
                store_state()
            except Exception as err:
                log_error("Error storing measurments locally, ignoring. Exception: " + str(err))

            log_debug("sending data to carbon cache")
            send_to_carbon(temp_dht, temp_maxin, humidity)

            if iterations >= 5:
                print_state()
                deepsleep()

            iterations += 1
            reset_holdoff_timer()
        except Exception as err:
            timeout_seconds = next_holdoff_seconds()
            log_error("Error in mainloop! (sleeping for "+ str(timeout_seconds) +"): " + str(err))
            # Errno 110 ETIMEOUT might be a sensor is not available or responding, check cables
            sleep(timeout_seconds)

init_wifi()
init_addr_info()
init_temp_sensor()
init_deepsleep()
init_time_via_ntp()
init_state()
reset_holdoff_timer()
blink()
log_debug('init done, starting main loop')

main_loop()

