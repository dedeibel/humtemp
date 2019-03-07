
DHT22_PIN = 12
TEMP_SENSOR_PIN = 13

ENTRIES_MEASURE_BATCH_SIZE = 1
SECONDS_BETWEEN_MEASUREMENTS = 0

# Max is about 3:30h https://thingpulse.com/max-deep-sleep-for-esp8266/
# 298: 5 Minutes, minus startup
DEEPSLEEP_SECONDS = 298
# Send every hour, that means every 12 measurement batches
ENTRIES_SEND_BATCH_SIZE = ENTRIES_MEASURE_BATCH_SIZE * 12
# ntp refresh in the same run as sending data so wifi is only initialized in that loop
# ntp is setup before the measurements so substract those values, sending is done
# after the measurements.
NTP_REFRESH_EACH_N_ITERATIONS = ENTRIES_SEND_BATCH_SIZE - ENTRIES_MEASURE_BATCH_SIZE
# dates are utc btw.
# TODO rename to "_N_ENTRIES"

ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS = 60

# Approx 117 bytes per entry, 135 Entries are < 16k (4 Blocks)
STATE_MAX_ENTRIES = 115
# When sending fails, old entries are kept. delete on overflow
DELETE_OLDER_ELEMENTS_COUNT_IF_MAX_REACHED = 30

DEBUG_LOG_ENABLED = $CONFIG_DEBUG_LOG_ENABLED

WIFI_ESSID = '$CONFIG_WIFI_ESSID'
WIFI_PASSWD = '$CONFIG_WIFI_PASSWD'

CARBON_HOST = '$CONFIG_CARBON_HOST'
CARBON_PORT = $CONFIG_CARBON_PORT
CARBON_DATA_PATH_PREFIX = '$CONFIG_CARBON_DATA_PATH_PREFIX'

STORAGE_FILENAME = 'db.dat'

# Faster times, use it to debug the cycle ...
#NTP_REFRESH_EACH_N_ITERATIONS = 1
#DEEPSLEEP_SECONDS = 5
#ENTRIES_SEND_BATCH_SIZE = 5
