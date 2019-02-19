import ujson

from configuration import *
from log import *

DATA_VERSION = 1
state = None

def build_state_entry(time, iteration):
    return {
            'time': time,
            'iteration': iteration,
            }

def set_measurement(state_entry, name, value):
    state_entry[name] = value

def append_state_entry(state_entry):
    global state
    state['entries'].append(state_entry)

def get_state_entries():
    return state['entries']

def state_entry_count():
    return len(state['entries'])

def init_state():
    log_debug('init state')
    global state
    _touch_file(STORAGE_FILENAME)
    _load_state()
    if not _is_version_valid():
        state = {'version': DATA_VERSION, 'entries': []}
    log_debug('state has %d entries' % (state_entry_count()))

def delete_older_state_entries():
    global state
    log_debug('purging older state entries %d to %d' % (state_entry_count(), DELETE_OLDER_ELEMENTS_COUNT_IF_MAX_REACHED))
    del state['entries'][:DELETE_OLDER_ELEMENTS_COUNT_IF_MAX_REACHED]
    log_debug('state has %d entries' % (state_entry_count()))

def state_entry_to_string(state_entry):
    return ujson.dumps(state_entry)

def truncate_state():
    global state
    state['entries'] = []
    store_state()

def _touch_file(file_path):
    with open(file_path, 'a') as db_file:
        pass

def _load_state():
    global state
    log_debug('loading db state')
    with open(STORAGE_FILENAME, 'r+') as db_file:
        try:
            state = ujson.load(db_file)
        except ValueError as ve:
            # might happen initially, start with empty state
            log_info('could not read state file, will start fresh')

def _is_version_valid():
    global state
    try:
        if state['version'] == DATA_VERSION:
            return True
    except:
        pass
    log_debug('version invalid, starting fresh')
    return False

def store_state():
    global state
    log_debug('storing current state, with %d entries' % (state_entry_count()))
    with open(STORAGE_FILENAME, 'w+') as db_file:
        try:
            ujson.dump(state, db_file)
        except Exception as e:
            log_error('could not store state file: %s' % (str(e)))

# does not obey log setting
def print_state():
    global state
    print('state')
    print(ujson.dumps(state))
