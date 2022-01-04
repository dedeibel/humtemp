
DHT22_PIN = 12
TEMP_SENSOR_PIN = 13

ENTRIES_SEND_BATCH_SIZE = 2
SECONDS_BETWEEN_MEASUREMENTS = 10
# -1 means no deepsleep, should not be smaller than send batch size
# or the data is lost
DEEPSLEEP_AFTER_ITERATIONS = 4

# Max is about 3:30h https://thingpulse.com/max-deep-sleep-for-esp8266/
# 298: 5 Minutes, minus startup
#DEEPSLEEP_SECONDS = 298
DEEPSLEEP_SECONDS = 60

NTP_UPDATE_TIME = True

ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS = 60

DEBUG_LOG_ENABLED = $CONFIG_DEBUG_LOG_ENABLED

WIFI_ESSID = '$CONFIG_WIFI_ESSID'
WIFI_PASSWD = '$CONFIG_WIFI_PASSWD'

CARBON_HOST = '$CONFIG_CARBON_HOST'
CARBON_PORT = $CONFIG_CARBON_PORT
CARBON_DATA_PATH_PREFIX = '$CONFIG_CARBON_DATA_PATH_PREFIX'

