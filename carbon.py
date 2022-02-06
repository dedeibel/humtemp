import usocket
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

        # udp (port 2003)
        #carbon_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        # tcp (port 2004)
        carbon_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # blocking io might be default but since I had problems with lost data
        # when sending data, closing socket and then deepsleeping, we make sure
        # here. Is not sufficient, only sleeping helped. what the...
        carbon_socket.setblocking(True)
       
        # UDP will not wait for the data to be sent before shutting down
        # the system. Data will get lost, setblocking does not help either.
        # Bug?
        
        carbon_socket.connect(carbon_addr[4])
        
        for entry in state_entries:
            try:
                _send_to_carbon(carbon_socket, entry)
                successfully_sent += 1
            except Exception as err:
                log_warning('Error sending entry (skipping): ' + str(err))

        carbon_socket.close()
        # make sure data is sent, it seems like also with TCP there is an issue
        # where the subsystem needs more time to send the data although we
        # called close. If we go to deepsleep now the data might not be send 
        sleep(1) 

        log_debug('sent %d entries to carbon server' % successfully_sent)

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
    time = state_entry['meta.time']
    for name, value in state_entry.items():
        # log_debug('sending data name: ' + str(name))
        _send_all(carbon_socket,
            '%s%s %.2f %d\n' % (CARBON_DATA_PATH_PREFIX, name, value, time))
        # Helps with sending UDP packets... should not be... I dont like it
        #sleep(1)

def _send_all(socket, msg):
    msglen = len(msg);
    totalsent = 0
    while totalsent < msglen:
        sent = socket.send(msg[totalsent:])
        # log_debug('sent: ' + str(sent) + " of: " + str(msglen))
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        totalsent = totalsent + sent

def _init_carbon_addr_info():
    global carbon_af
    global carbon_addr
    if carbon_addr != None:
        log_debug('carbon addr already present, skipping init')
        return

    carbon_addr = usocket.getaddrinfo(CARBON_HOST, CARBON_PORT, usocket.SOCK_DGRAM)[0]
    # OS Error 2 here means host not found / resolvable
    log_debug('init addr info done, sending data to ' + CARBON_HOST + ':' + str(CARBON_PORT))

