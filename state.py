import ujson

from configuration import *
from log import *
from linestore import *

DATA_VERSION = 1
state = []

def build_state_entry(time, iteration, temp_dht, humidity, temp1, temp2, temp3):
    return {
            'time': time,
            'iteration': iteration,
            'temp_dht': temp_dht,
            'humidity': humidity,
            'temp1': temp1,
            'temp2': temp2,
            'temp3': temp3}

def append_state_entry(state_entry):
    global state
    state.append(state_entry)

    with Linestore(STORAGE_FILENAME) as linestore:
        linestore.append(DATA_VERSION, _export_line(state_entry))

def get_state_entries():
    return state

def state_entry_count():
    global state
    return len(state)

def init_state():
    log_debug('loading db state')
    with Linestore(STORAGE_FILENAME) as linestore:
        _import_all(linestore.readlines(DATA_VERSION))

    log_debug('state has %d entries' % (state_entry_count()))

def _import_all(line_arrays):
    for line in line_arrays:
        _import(line)

def _import(line):
    global state
    state.append(
        build_state_entry(line[0], line[1], line[2], line[3], line[4], line[5], line[6]))

def _export_line(state_entry):
    return [state_entry['time'],
            state_entry['iteration'],
            state_entry['temp_dht'],
            state_entry['humidity'],
            state_entry['temp1'],
            state_entry['temp2'],
            state_entry['temp3']]

def truncate_state():
    Linestore(STORAGE_FILENAME).truncate()

# does not obey log setting
def print_state():
    global state
    print('state')
    print(ujson.dumps(state))
