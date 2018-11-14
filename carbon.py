import socket
import uerrno

from configuration import *
from log import *
from state import *
from wifi import *

carbon_addr = None

# service
def send_state_to_carbon():
    try:
        log_debug('sending data to carbon cache')
        init_wifi()
        _init_carbon_addr_info()
        successfully_sent = 0

        state_entries = get_state_entries()

        carbon_socket = socket.socket()
        carbon_socket.connect(carbon_addr)
        
        for entry in state_entries:
            try:
                _send_to_carbon(carbon_socket, entry)
                successfully_sent += 1
            except Exception as err:
                log_warning('Error sending entry, (skipping): ' + str(err))

        carbon_socket.close()

        log_info('sent %d entries to carbon server' % successfully_sent)

        if successfully_sent == 0:
            raise ValueError('Could not send any entries to carbon, see previous errors')
    except OSError as socket_error:
        if socket_error.args[0] == uerrno.ECONNRESET:
            raise ValueError('Could not send any entries to carbon, connection reset')
        elif socket_error.args[0] == uerrno.ECONNREFUSED:
            raise ValueError('Could not send any entries to carbon, connection refused')
        else:
            raise

def _send_to_carbon(carbon_socket, state_entry):
    time = state_entry['unix_time']
    carbon_socket.send('test.heidestock.iteration %.2f %d\n' % (state_entry['iteration'], time))
    carbon_socket.send('test.heidestock.temp.a %.2f %d\n' % (state_entry['temp_dht'], time))
    carbon_socket.send('test.heidestock.temp.b %.2f %d\n' % (state_entry['temp_maxin'], time))
    carbon_socket.send('test.heidestock.humidity %.2f %d\n' % (state_entry['humidity'], time))

def _init_carbon_addr_info():
    global carbon_addr
    if carbon_addr != None:
        log_debug('carbon addr already present, skipping init')
        return

    carbon_addr_info = socket.getaddrinfo(CARBON_HOST, CARBON_PORT)
    # OS Error 2 here means host not found / resolvable

    carbon_addr = carbon_addr_info[0][-1]
    log_debug('init addr info done, sending data to ' + CARBON_HOST + ':' + str(CARBON_PORT))
