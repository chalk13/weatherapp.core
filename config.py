"""Constants for the weather application project."""

ACCU_PROVIDER_NAME = 'accu'  # provider id
RP5_PROVIDER_NAME = 'rp5'  # provider id

ACCU_PROVIDER_TITLE = 'AccuWeather'  # provider title
RP5_PROVIDER_TITLE = 'RP5'  # provider title

FAKE_MOZILLA_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'

DEFAULT_NAME = 'Kyiv'
DEFAULT_URL_ACCU = 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505'
DEFAULT_URL_RP5 = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'
BROWSE_LOCATIONS = {'accu': 'https://www.accuweather.com/en/browse-locations',
                    'rp5': 'http://rp5.ua/Weather_in_the_world'}

CONFIG_FILE = 'weatherapp.ini'
CONFIG_LOCATION = 'Location'
CACHE_DIR = '.weatherappcache'
CACHE_TIME = 900
DAY_IN_SECONDS = 86400
