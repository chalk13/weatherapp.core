"""Constants for the weather application project."""

# application default verbose and log levels
DEFAULT_VERBOSE_LEVEL = 0

FAKE_MOZILLA_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'

# AccuWeather provider related configuration
ACCU_PROVIDER_NAME = 'accu'  # provider id
ACCU_PROVIDER_TITLE = 'AccuWeather'  # provider title
DEFAULT_URL_ACCU = 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505'

# RP5 provider related configuration
RP5_PROVIDER_NAME = 'rp5'  # provider id
RP5_PROVIDER_TITLE = 'RP5'  # provider title
DEFAULT_URL_RP5 = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'

# SINOPTIK provider related configuration
SINOPTIK_PROVIDER_NAME = 'sinoptik'  # provider id
SINOPTIK_PROVIDER_TITLE = 'SINOPTIK'  # provider title
DEFAULT_URL_SINOPTIK = 'https://ua.sinoptik.ua/погода-київ'

DEFAULT_NAME = 'Kyiv'  # default location, common for each provider
BROWSE_LOCATIONS = {'accu': 'https://www.accuweather.com/en/browse-locations',
                    'rp5': 'http://rp5.ua/Weather_in_the_world',
                    'sinoptik': 'https://ua.sinoptik.ua//погода-європа'}

CONFIG_FILE = 'weatherapp.ini'  # configuration file name

# Cache settings
CACHE_DIR = '.weatherappcache'  # cache directory name
CACHE_TIME = 900  # how long cache files are valid (in seconds)
DAY_IN_SECONDS = 86400  # time during which the cache is not removed
