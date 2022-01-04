import ujson

from configuration import *
from log import *

state = {}

# state entries contain tag info and values
# source.measurement => value
def build_state_entry(time, iteration):
    return {
            'meta.time': time,
            'meta.iteration': iteration,
            }

def set_measurement(state_entry, sensor, measurement, value):
    state_entry[sensor +'.'+ measurement] = value

def set_meta(state_entry, name, value):
    state_entry['meta.'+ name] = value

def append_state_entry(state_entry):
    global state
    state['entries'].append(state_entry)

def get_state_entries():
    return state['entries']

def state_entry_count():
    return len(state['entries'])

def init_state():
    log_debug('init state')
    truncate_state()

def state_entry_to_string(state_entry):
    return ujson.dumps(state_entry)

def truncate_state():
    global state
    state['entries'] = []

# does not obey log setting
def print_state():
    global state
    print('state')
    print(ujson.dumps(state))

