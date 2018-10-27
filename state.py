import ujson

from configuration import *
from log import *

state = None

def build_state_entry(time, iteration, temp_dht, temp_maxin, humidity):
    return {'time': time, 'iteration': iteration, 'temp_dht': temp_dht, 'temp_maxin': temp_maxin, 'humidity': humidity}

def append_state_entry(state_entry):
    global state
    state.append(state_entry)

def get_state_entries():
    return state

def state_entry_count():
    global state
    return len(state)

def init_state():
    delete_state_entries()
    _touch_file(STORAGE_FILENAME)
    _load_state()
    log_debug('state has %d entries' % (state_entry_count()))

def delete_state_entries():
    global state
    state = []

def delete_older_state_entries():
    global state
    log_debug('purging older state entries %d to %d' % (state_entry_count(), DELETE_OLDER_ELEMENTS_COUNT_IF_MAX_REACHED))
    del state[:DELETE_OLDER_ELEMENTS_COUNT_IF_MAX_REACHED]

def _touch_file(file_path):
    db_file = open(file_path, 'a')
    db_file.close()

def _load_state():
    log_debug('loading db state')
    global state
    state = _do_load_state()

def _do_load_state():
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
    log_debug('storing current state, with %d entries' % (state_entry_count()))
    db_file = open(STORAGE_FILENAME, 'w+')
    try:
        ujson.dump(state, db_file)
    finally:
        db_file.close()

# does not obey log setting
def print_state():
    global state
    print('state')
    print(ujson.dumps(state))
