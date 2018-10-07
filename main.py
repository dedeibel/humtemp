from time import sleep
import network
import socket
import machine
import dht
import onewire, ds18x20

WIFI_ESSID = $CONFIG_WIFI_ESSID
WIFI_PASSWD = $CONFIG_WIFI_PASSWD
CARBON_HOST = $CONFIG_CARBON_HOST
CARBON_PORT = $CONFIG_CARBON_PORT

DEEPSLEEP_MS = 30000

DHT22_PIN = 12
TEMP_SENSOR_PIN = 13

dht22 = dht.DHT22(machine.Pin(DHT22_PIN))
ledpin = machine.Pin(0, machine.Pin.OUT)

rtc = None
ds = None
roms = None
carbon_addr = None

#
# temp sensor
#

def init_temp_sensor():
    global ds
    global roms

    dat = machine.Pin(TEMP_SENSOR_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    roms = ds.scan()
    print('init temp sensor done, found onewire devices:', roms)

def do_onewire_reading():
    ds.convert_temp()
    # we sleep anyway for beeping in the main loop
    # time.sleep_ms(750)

def read_first_onewire_temp():
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
        print('connecting to network '+ WIFI_ESSID + ' ...')
        sta_if.active(True)
        sta_if.connect(WIFI_ESSID, WIFI_PASSWD)
        while not sta_if.isconnected():
            sleep(.3)
            print('waiting ...')
            pass
    print('init wifi done, network config:', sta_if.ifconfig())

def init_addr_info():
    global carbon_addr

    carbon_addr_info = socket.getaddrinfo(CARBON_HOST, CARBON_PORT)
    carbon_addr = carbon_addr_info[0][-1]
    print('init addr info done, sending data to ' + CARBON_HOST + ':' + str(CARBON_PORT))

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
        print('woke from a deep sleep')
    else:
        print('power on or hard reset')

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    print('init deepsleep done')

def deepsleep():
    print('going to deepsleep for: '+ str(DEEPSLEEP_MS))
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
# utility
#

def holdoff(previous_seconds):
    if previous_seconds > 60:
        return 60
    else:
        return previous_seconds * 2

def print_results(temp_dht, temp_maxin, humidity):
    print("temp_dht: {:.1f} *C \t temp_maxin: {:.1f} *C \t humidity: {}%".format(
        temp_dht, temp_maxin, humidity))

def main_loop():
    err_timeout = 1
    iterations = 1
    while True:
        try:
            dht22.measure()
            led_on()
            do_onewire_reading()
            led_off()
            ledpin.value(1)
            sleep(1)
            # sleeping at least 1 sec
            temp_dht = dht22.temperature()
            temp_maxin = read_first_onewire_temp()
            humidity = dht22.humidity()
            print_results(temp_dht, temp_maxin, humidity)
            send_to_carbon(temp_dht, temp_maxin, humidity)

            if iterations >= 5:
                deepsleep()

            iterations += 1
            err_timeout = 1
        except Exception as err:
            print("Error (sleeping for "+ str(err_timeout) +"): " + str(err))
            err_timeout = holdoff(err_timeout)
            sleep(err_timeout)

init_wifi()
init_addr_info()
init_temp_sensor()
init_deepsleep()
blink()
print('init done, starting main loop')
main_loop()


# TODO
# - use ntp
# - store sensor values on nvram
# - reuse time / check deepsleep accuracy
#
#

