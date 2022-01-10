
DHT22_PIN = const(12)
TEMP_SENSOR_PIN = const(13)

#ENTRIES_SEND_BATCH_SIZE = const(1)
# -1 means no deepsleep, should not be smaller than send batch size
# or the data is lost
#DEEPSLEEP_AFTER_ITERATIONS = const(1)
# Irrelevant if deepsleep after iterations is 1
#SECONDS_BETWEEN_MEASUREMENTS = const(900) # 15 minutes

# Max is about 3:30h https://thingpulse.com/max-deep-sleep-for-esp8266/
# 298: 5 Minutes, minus 2 seconds startup
#DEEPSLEEP_SECONDS = const(898) # 15 minutes

# Settings for debugging
ENTRIES_SEND_BATCH_SIZE = const(1)
SECONDS_BETWEEN_MEASUREMENTS = const(10)
DEEPSLEEP_AFTER_ITERATIONS = const(5)
DEEPSLEEP_SECONDS = const(15)

NTP_UPDATE_TIME = True

READ_BATTERY_FROM_ADC = True

ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS = const(60)

DEBUG_LOG_ENABLED = $CONFIG_DEBUG_LOG_ENABLED

WIFI_ESSID = '$CONFIG_WIFI_ESSID'
WIFI_PASSWD = '$CONFIG_WIFI_PASSWD'

CARBON_HOST = '$CONFIG_CARBON_HOST'
CARBON_PORT = const($CONFIG_CARBON_PORT)
CARBON_DATA_PATH_PREFIX = '$CONFIG_CARBON_DATA_PATH_PREFIX'

