from time import sleep
import network

from configuration import *
from log import *

wifi_initialized = False
sta_if = None

def init_wifi():
    global wifi_initialized
    global sta_if

    if wifi_initialized:
        log_debug('wifi already initialized, skipping init')
        return

    log_debug('initializing network')

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    attempts = 10
    if not sta_if.isconnected():
        log_debug('connecting to network '+ WIFI_ESSID + ' ...')
        if WIFI_USE_STATIC_IP:
            sta_if.ifconfig((WIFI_IP, WIFI_NETMASK, WIFI_GATEWAY, WIFI_DNS_SERVER))
        sta_if.connect(WIFI_ESSID, WIFI_PASSWD)
        while not sta_if.isconnected() and attempts > 0:
            attempts -= 1
            log_debug('waiting ...')
            sleep(2) # it usually took about three seconds
            pass

    if attempts <= 0:
        raise Exception("Could not connect to network")

    wifi_initialized = True
    log_debug('init wifi done, network config: ' + str(sta_if.ifconfig()))

def wifi_disconnect():
    global sta_if
    if sta_if.isconnected():
        log_debug('disconnecting wifi')
        sta_if.disconnect()
