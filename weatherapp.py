"""Weather application project.

Resources: AccuWeather, Rp5, Sinoptik
Packages: urllib
"""
import html
import re
from urllib.request import urlopen, Request


def get_request_headers():
    """Return information for headers"""

    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'}


def get_page_from_server(page_url: str) -> str:  # getting page from server
    """Return information about the page in the string format"""

    request = Request(page_url, headers=get_request_headers())
    page = urlopen(request).read()

    return page.decode('utf-8')


def get_tag_info(tag: str, page: str) -> str:
    """Return information that has a tag"""

    # finding the place where tag is located
    tag_size = len(tag)
    tag_index = page.find(tag)
    start_value = tag_size + tag_index

    result = ''
    for item in page[start_value:]:
        if item != '<':
            result += item
        else:
            break

    return result


def get_weather_info(page, tags):
    """Return information collected from tags"""

    return tuple(get_tag_info(tag, page) for tag in tags)


def program_output(weather_site, location, temp, condition):
    """Print the application output in readable form"""

    print(f'{weather_site}:')
    print(f'Location: {location}')
    print(f'Temperature: {html.unescape(temp)}\nCurrent state: {condition}')


def main():
    """Main entry point"""

    weather_sites = {'ACCUWEATHER': (ACU_URL, ACU_TAGS),
                     'RP5': (RP5_URL, RP5_TAGS),
                     'SINOPTIK': (SIN_URL, SIN_TAGS)}
    for site in weather_sites:
        url, tags = weather_sites[site]
        content = get_page_from_server(url)
        location, temp, condition = get_weather_info(content, tags)
        program_output(site, location, temp, condition)


# start pages for getting information
ACU_URL = 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505'
RP5_URL = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'
SIN_URL = 'https://ua.sinoptik.ua'

# ACU tags info: location, temp, condition
ACU_TAGS = {'<span class="current-city"><h1>',
            '<span class="large-temp">',
            '<span class="cond">'}
# RP5 tags info: location, temp, condition

# through constant changes - use regular expression to get status information
CONDITION_RESULT = re.search(r'<div class="..." onmouseover="tooltip\(this, \'<b>',
                             get_page_from_server(RP5_URL))

RP5_TAGS = {'<div id="pointNavi"><h1>',
            '<span class="t_0" style="display: block;">',
            CONDITION_RESULT.group(0)}
# Sinoptik tags info: location, temp, condition
SIN_TAGS = {'<h1 class="isMain"> <strong>Погода</strong>',
            '<p class="today-temp">',
            '<div class="description"> <!--noindex-->'}


if __name__ == '__main__':
    main()
