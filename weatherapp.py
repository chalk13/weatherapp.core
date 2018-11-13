"""Weather application project.

Resources: AccuWeather, Rp5
Packages: urllib
"""
import html
from urllib.request import urlopen, Request

# start pages for getting information
ACU_URL = "https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505"
RP5_URL = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'


def get_page_from_server(page_url: str) -> str:  # getting page from server
    """Return information about the page in the string format"""

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'}
    request = Request(page_url, headers=headers)
    page = urlopen(request).read()

    return str(page)


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


acu_page = get_page_from_server(ACU_URL)
rp5_page = get_page_from_server(RP5_URL)

# ACCU weather tags info: location, temp, condition
ACU_TAGS = {'location': '<span class="current-city"><h1>',
            'temp': '<span class="large-temp">',
            'condition': '<span class="cond">'}
# RP5 weather tags info: location, temp, wind
RP5_TAGS = {'location': '<div id="pointNavi"><h1>',
            'temp': '<span class="t_0" style="display: block;">',
            'wind': '<span class="wv_0" style="">'}

acu_location = get_tag_info(ACU_TAGS['location'], acu_page)
acu_temp = get_tag_info(ACU_TAGS['temp'], acu_page)
acu_condition = get_tag_info(ACU_TAGS['condition'], acu_page)

rp5_location = get_tag_info(RP5_TAGS['location'], rp5_page)
rp5_temp = get_tag_info(RP5_TAGS['temp'], rp5_page)
rp5_wind = get_tag_info(RP5_TAGS['wind'], rp5_page)

print("AccuWeather website info:\n------------------------")
print(f"Location: {acu_location}")
print(f"Temperature: {html.unescape(acu_temp)}\nCurrent state: {acu_condition}")

print("\nRP5 website info:\n----------------")
print(f"Location: {rp5_location}")
print(f"Temperature: {html.unescape(rp5_temp)}\nWind: {rp5_wind}")
