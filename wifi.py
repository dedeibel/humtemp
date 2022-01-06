from time import sleep
import network

from configuration import *
from log import *

wifi_initialized = False
sta_if = None

def init_wifi():
    global wifi_initialized
    if wifi_initialized:
        log_debug('wifi already initialized, skipping init')
        return

    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log_debug('connecting to network '+ WIFI_ESSID + ' ...')
        sta_if.active(True)
        # TODO set static IP here sta_if.ifconfig(('xxx.xxx.xxx.xxx','255.255.255.0','192.168.1.1','xxx.xxx.xxx.xxx'))
        sta_if.connect(WIFI_ESSID, WIFI_PASSWD)
        while not sta_if.isconnected():
            sleep(.3)
            log_debug('waiting ...')
            pass

    wifi_initialized = True
    log_debug('init wifi done, network config: ' + str(sta_if.ifconfig()))

def wifi_disconnect():
    global sta_if
    if sta_if.isconnected():
        log_debug('disconnecting wifi')
        sta_if.disconnect()
