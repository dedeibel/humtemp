
DHT22_PIN = const(12)
TEMP_SENSOR_PIN = const(13)

ENTRIES_SEND_BATCH_SIZE = const(1)
# -1 means no deepsleep, should not be smaller than send batch size
# or the data is lost
DEEPSLEEP_AFTER_ITERATIONS = const(1)
# Irrelevant if deepsleep after iterations is 1
SECONDS_BETWEEN_MEASUREMENTS = const(900) # 15 minutes

# Max is about 3:30h https://thingpulse.com/max-deep-sleep-for-esp8266/
# 298: 5 Minutes, minus 2 seconds startup
DEEPSLEEP_MS = const(898000) # 15 minutes

ERROR_TIMEOUT_HOLDOFF_MAX_SECONDS = const(60)

# Settings for debugging, make sure the other values are commented out 
#ENTRIES_SEND_BATCH_SIZE = const(1)
#SECONDS_BETWEEN_MEASUREMENTS = const(15)
#DEEPSLEEP_AFTER_ITERATIONS = const(3)
#DEEPSLEEP_MS = const(20000)

# Otherwise only on hard boot
NTP_SKIP_AFTER_DEEPSLEEP = False

DEBUG_LOG_ENABLED = $CONFIG_DEBUG_LOG_ENABLED

WIFI_ESSID = '$CONFIG_WIFI_ESSID'
WIFI_PASSWD = '$CONFIG_WIFI_PASSWD'

WIFI_USE_STATIC_IP = True
WIFI_IP = '$CONFIG_WIFI_IP'
WIFI_NETMASK = '$CONFIG_WIFI_NETMASK'
WIFI_GATEWAY = '$CONFIG_WIFI_GATEWAY'
WIFI_DNS_SERVER = '$CONFIG_WIFI_DNS_SERVER'

CARBON_HOST = '$CONFIG_CARBON_HOST'
CARBON_PORT = const($CONFIG_CARBON_PORT)
CARBON_DATA_PATH_PREFIX = '$CONFIG_CARBON_DATA_PATH_PREFIX'

READ_BATTERY_FROM_ADC = True

# As per spec https://docs.micropython.org/en/latest/esp8266/quickref.html#adc-analog-to-digital-conversion
# adc_max_val = const(1023)
# factor to get mV
# 1 / adc_max_val
# times 1000 for mV
ADC_FACTOR_ONE_OVER = 0.9775
# Add to adc mV result
ADC_OFFSET_MV = const(0)

# 1 MOhm vs 220 kOhm voltage divider
# battery_factor = 0.18033
# 1 / battery_factor
BATTERY_FACTOR_ONE_OVER = 5.545454

# 47 kOhm vs 10 kOhm voltage divider
# battery_factor = 0.17544
# 1 / battery_factor
# battery_factor_one_over = 5.7

# adc_min_working_val = 0.65 # by experiment
