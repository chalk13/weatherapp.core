"""Weather application project.

Resources: AccuWeather, RP5
Packages: urllib
"""
import argparse
import configparser
import csv
import hashlib
import html
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

DEFAULT_NAME = 'Kyiv'
DEFAULT_URL = {'accu': 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505',
               'rp5': 'http://rp5.ua/Weather_in_Kiev,_Kyiv'}
BROWSE_LOCATIONS = {'accu': 'https://www.accuweather.com/en/browse-locations',
                    'rp5': 'http://rp5.ua/Weather_in_the_world'}
CONFIG_LOCATION = 'Location'
CONFIG_FILE = 'weatherapp.ini'
CACHE_DIR = '.weatherappcache'
CACHE_TIME = 900


def get_request_headers() -> dict:
    """Return information for headers"""

    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'}


def get_cache_directory():
    """Return path to the cache directory"""

    return Path.home() / CACHE_DIR


def cache_is_valid(path):
    """Check if current cache file is valid"""

    return (time.time() - path.stat().st_mtime) < CACHE_TIME


def get_url_hash(url: str) -> str:
    """Generates hash for given url"""

    return hashlib.md5(url.encode('utf-8')).hexdigest()


def save_cache(url: str, page_source: str):
    """Save page source data to file"""

    url_hash = get_url_hash(url)
    cache_dir = get_cache_directory()
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    with (cache_dir/url_hash).open('wb') as cache_file:
        cache_file.write(page_source)


def get_cache(url: str):
    """Return cache data if any exists"""

    cache = b''
    url_hash = get_url_hash(url)
    cache_dir = get_cache_directory()
    if cache_dir.exists():
        cache_path = cache_dir / url_hash
        if cache_path.exists() and cache_is_valid(cache_path):
            with cache_path.open('rb') as cache_file:
                cache = cache_file.read()

    return cache


def get_page_from_server(page_url: str) -> str:  # getting page from server
    """Return information about the page in the string format"""

    cache = get_cache(page_url)
    if cache:
        page = cache
    else:
        request = Request(page_url, headers=get_request_headers())
        page = urlopen(request).read()
        save_cache(page_url, page)

    return page.decode('utf-8')


def get_locations_accu(locations_url: str) -> list:
    """Return a list of locations and related urls"""

    locations_page = get_page_from_server(locations_url)
    soup = BeautifulSoup(locations_page, 'html.parser')

    locations = []
    for location in soup.find_all('li', class_='drilldown cl'):
        url = location.find('a').attrs['href']
        location = location.find('em').text
        locations.append((location, url))
    return locations


def get_locations_rp5(locations_url: str) -> list:
    """Return a list of locations and related urls"""

    locations_page = get_page_from_server(locations_url)
    soup = BeautifulSoup(locations_page, 'html.parser')

    locations = []
    # TODO: try rewrite logic in an easier way
    places = soup.find_all('div', class_='country_map_links')
    if not places:
        places = soup.find_all('a', class_='href20')
        if not places:
            places = soup.find_all('div', class_='city_link')
            for place in places:
                url = place.find('a').attrs['href']
                url = f'http://rp5.ua/{url}'
                location = place.text
                locations.append((location, url))
                return locations
        for place in places:
            url = place.attrs['href']
            url = f'http://rp5.ua/{url}'
            location = place.text
            locations.append((location, url))
        return locations
    else:
        for location in places:
            url = location.find('b')
            url = url.find('a').attrs['href']
            url = f'http://rp5.ua{url}'
            location = location.find('b').text[:-1]
            locations.append((location, url))
        return locations


def get_configuration_file():
    """Return path to the CONFIG_FILE"""

    return Path.home() / CONFIG_FILE


def save_configuration(name: str, url: str):
    """Write the location to the configfile"""

    parser = configparser.ConfigParser()
    parser[CONFIG_LOCATION] = {'name': name, 'url': url}
    with open(get_configuration_file(), 'w') as configfile:
        parser.write(configfile)


def get_configuration(command: str) -> tuple:
    """Return name of the city and related url"""

    name = DEFAULT_NAME
    url = DEFAULT_URL[command]

    parser = configparser.ConfigParser()
    parser.read(get_configuration_file())

    if CONFIG_LOCATION in parser.sections():
        config = parser[CONFIG_LOCATION]
        name, url = config['name'], config['url']

    return name, url


def configuration(command: str):
    """Set the location for which to display the weather"""

    if command == 'accu':
        locations = get_locations_accu(BROWSE_LOCATIONS[command])
    elif command == 'rp5':
        locations = get_locations_rp5(BROWSE_LOCATIONS[command])

    while locations:
        for index, location in enumerate(locations):
            print(f'{index + 1}) {location[0]}')
        selected_index = int(input('Please select location: '))
        location = locations[selected_index - 1]
        if command == 'accu':
            locations = get_locations_accu(location[1])
        elif command == 'rp5':
            locations = get_locations_rp5(location[1])

    save_configuration(*location)


def get_weather_accu(page: str) -> dict:
    """Return information collected from AccuWeather"""

    weather_page = BeautifulSoup(page, 'html.parser')
    current_day_selection = weather_page.find('li', {'class': ['day current first cl',
                                                               'night current first cl']})

    weather_info = {}
    if current_day_selection:
        current_day_url = current_day_selection.find('a').attrs['href']
        if current_day_url:
            current_day_page = get_page_from_server(current_day_url)
            if current_day_page:
                current_day = BeautifulSoup(current_day_page, 'html.parser')
                weather_details = current_day.find('div', attrs={'id': 'detail-now'})
                temp = weather_details.find('span', class_='large-temp')
                if temp:
                    weather_info['Temperature'] = temp.text
                condition = weather_details.find('span', class_='cond')
                if condition:
                    weather_info['Condition'] = condition.text

                feel_temp = weather_details.find('span', class_='small-temp')
                if feel_temp:
                    weather_info['RealFeel'] = feel_temp.text
                wind_info = weather_details.find_all('li', class_='wind')
                if wind_info:
                    weather_info['Wind'] = ' '.join(map(lambda t: t.text.strip(), wind_info))

    return weather_info


def get_weather_rp5(page: str) -> dict:
    """Return information collected from RP5"""

    weather_page = BeautifulSoup(page, 'html.parser')
    current_day_temperature = weather_page.find('div', class_='ArchiveTemp')
    current_day_weather_details = weather_page.find('div', id='forecastShort-content')

    weather_info = {}
    if current_day_temperature:
        temperature = current_day_temperature.find('span', class_='t_0')
        if temperature:
            weather_info['Temperature'] = temperature.text
    if current_day_weather_details:
        condition = current_day_weather_details.find('b')
        if condition:
            start_cond = condition.text.find(',', condition.text.find(',') + 1) + 2
            end_cond = condition.text.find(',', start_cond + 1)
            weather_info['Condition'] = condition.text[start_cond:end_cond]
        today_expect = current_day_weather_details.find('span', class_='t_0')
        if today_expect:
            weather_info['Expect'] = today_expect.text[:-3]
        if condition:
            first_sentence_end = condition.text.find('. ')
            first_sentence = condition.text[:first_sentence_end]
            start = first_sentence.rfind(',') + 2
            weather_info['Wind'] = first_sentence[start:]

    return weather_info


def get_weather_info_to_save(command: str) -> dict:
    """Return information from weather site to save"""

    if command == 'accu':
        city_name, content = get_city_name_page_content(command)
        weather_info = get_weather_accu(content)
    if command == 'rp5':
        city_name, content = get_city_name_page_content(command)
        weather_info = get_weather_rp5(content)

    return weather_info


def write_info_to_csv(command: str):
    """Write data to a CSV file"""

    info = get_weather_info_to_save(command)

    output_file = open('weather_data.csv', 'w', newline='')
    output_writer = csv.writer(output_file)
    output_writer.writerow(['Parameters', 'Description'])
    for key, value in info.items():
        output_writer.writerow([key, value])
    output_file.close()


def program_output(city: str, info: dict):
    """Print the application output in readable form"""

    length_column_1 = max(len(key) for key in info.keys())
    length_column_2 = max(len(value) for value in info.values())

    print(f'{city.upper()}')

    def border_line(column_1: int, column_2: int) -> str:
        """Print a line for dividing information"""

        line = ''.join(['+'] + ['-' * (column_1 + column_2 + 5)] + ['+'])
        return line

    def status_msg(msg: str, state: str) -> str:
        """Print weather information"""

        result = f"| {msg} {' ' * (length_column_1 - len(msg))}" \
                 f"| {state} {' ' * (length_column_2 - len(state))}|\n"
        return result

    print(border_line(length_column_1, length_column_2))

    for key, value in info.items():
        print(status_msg(key, html.unescape(value)), end='')

    print(border_line(length_column_1, length_column_2))


def get_city_name_page_content(command: str) -> tuple:
    """Return name of the city and page content"""

    city_name, city_url = get_configuration(command)
    content = get_page_from_server(city_url)
    return city_name, content


def get_weather_info(command: str):
    """Function to get weather info"""

    city_name, content = get_city_name_page_content(command)

    if command == 'accu':
        try:
            print(f'Information from {command.upper()} weather site:')
            program_output(city_name, get_weather_accu(content))
        except ValueError:
            print("Please, first change the configuration file for AccuWeather.\n"
                  "Use the following command: config_accu")
    if command == 'rp5':
        try:
            print(f'Information from {command.upper()} weather site:')
            program_output(city_name, get_weather_rp5(content))
        except ValueError:
            print("Please, first change the configuration file for RP5.\n"
                  "Use the following command: config_rp5")


def main(argv):
    """Main entry point"""

    known_commands = {'accu': get_weather_info,
                      'rp5': get_weather_info,
                      'config_accu': configuration,
                      'config_rp5': configuration,
                      'save_to_csv_accu': write_info_to_csv,
                      'save_to_csv_rp5': write_info_to_csv}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to choose weather website', nargs=1)
    params = parser.parse_args(argv)

    if params.command:
        command = params.command[0]
        if command in known_commands:
            command_site = command.split('_')[-1]
            known_commands[command](command_site)
        else:
            print('Unknown command provided.')
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
