from configuration import *

def log(message):
    print(message)

def log_debug(message):
    if DEBUG_LOG_ENABLED:
        log(message)

# allow filtering using preprocessor

def log_info(message):
    log(message)

def log_warning(message):
    log(message)

def log_error(message):
    log(message)
