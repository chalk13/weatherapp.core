"""Weather application project.

Resources: AccuWeather, Rp5
Packages: urllib
"""
import html
from urllib.request import urlopen, Request

# start page for information
ACCU_URL = "https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505"

# getting page from server
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'}
accu_request = Request(ACCU_URL, headers=headers)
accu_page = urlopen(accu_request).read()
accu_page = str(accu_page)

ACCU_LOCATION = '<span class="current-city"><h1>'
ACCU_TEMP_TAG = '<span class="large-temp">'
ACCU_CONDITION = '<span class="cond">'


def get_tag_info(tag: str, page: str) -> str:
    """Return information that has a tag"""

    # finding the place where temp_tag is located
    tag_size = len(tag)
    tag_index = page.find(tag)
    start_value = tag_size + tag_index

    result = ''
    for item in page[start_value:]:
        if item != "<":
            result += item
        else:
            break

    return result


accu_location = get_tag_info(ACCU_LOCATION, accu_page)
accu_temp = get_tag_info(ACCU_TEMP_TAG, accu_page)
accu_condition = get_tag_info(ACCU_CONDITION, accu_page)

print("AccuWeather:\n")
print(f"The weather in {accu_location}")
print(f"Temperature: {html.unescape(accu_temp)}\nCurrent state: {accu_condition}")
