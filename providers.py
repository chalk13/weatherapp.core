"""Weather providers for the weather application project.

This file includes classes for each weather service provider.
Providers: accuweather.com, rp5.ua
"""

import configparser
import hashlib
import os
import shutil
import time
from pathlib import Path
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

import config


class WeatherProvider:
    """Base weather provider"""


class AccuWeatherProvider:

    """Weather provider for AccuWeather site.
    """

    def __init__(self, command=None):
        self.name = config.ACCU_PROVIDER_NAME

        if command is not None:
            location, url = self.get_configuration(command)
            self.location = location
            self.url = url

    def get_configuration_file(self):
        """Path to the CONFIG_FILE.

        Returns path to configuration file in your home directory.
        """

        return Path.home() / config.CONFIG_FILE

    def save_configuration(self, command: str, name: str, url: str):
        """Write the location to the configfile"""

        parser = configparser.ConfigParser()
        parser[command] = {'name': name, 'url': url}
        with open(self.get_configuration_file(), 'w') as configfile:
            parser.write(configfile)

    def get_configuration(self, command: str) -> tuple:
        """Returns name of the city and related url"""

        name = config.DEFAULT_NAME
        url = config.DEFAULT_URL[command]

        parser = configparser.ConfigParser()
        parser.read(self.get_configuration_file())

        if command in parser.sections():
            configuration = parser[command]
            name, url = configuration['name'], configuration['url']

        return name, url

    def get_request_headers(self) -> dict:
        """Return information for headers"""

        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    def get_cache_directory(self):
        """Return path to the cache directory"""

        return Path.home() / config.CACHE_DIR

    def cache_is_valid(self, path) -> bool:
        """Check if current cache file is valid"""

        return (time.time() - path.stat().st_mtime) < config.CACHE_TIME

    def get_url_hash(self, url: str) -> str:
        """Generates hash for given url"""

        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def save_cache(self, url: str, page_source: str):
        """Save page source data to file"""

        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
        with (cache_dir / url_hash).open('wb') as cache_file:
            cache_file.write(page_source)

    def get_cache(self, url: str):
        """Return cache data if any exists"""

        cache = b''
        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            cache_path = cache_dir / url_hash
            if cache_path.exists() and self.cache_is_valid(cache_path):
                with cache_path.open('rb') as cache_file:
                    cache = cache_file.read()

        return cache

    def clear_app_cache(self):
        """Delete directory with cache"""

        cache_dir = self.get_cache_directory()
        shutil.rmtree(cache_dir)

    def delete_invalid_cache(self):
        """Delete all invalid (old) cache"""

        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            path = Path(cache_dir)
            dirs = os.listdir(path)
            for file in dirs:
                life_time = time.time() - (path / file).stat().st_mtime
                if life_time > config.DAY_IN_SECONDS:
                    os.remove(path / file)

    def get_page_from_server(self, page_url: str, refresh: bool = False) -> str:
        """Return information about the page in the string format"""

        cache = self.get_cache(page_url)
        if cache and not refresh:
            page = cache
        else:
            request = Request(page_url, headers=self.get_request_headers())
            page = urlopen(request).read()
            self.save_cache(page_url, page)

        return page.decode('utf-8')

    def get_locations_accu(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls"""

        locations_page = self.get_page_from_server(locations_url, refresh=refresh)
        soup = BeautifulSoup(locations_page, 'html.parser')

        locations = []
        for location in soup.find_all('li', class_='drilldown cl'):
            url = location.find('a').attrs['href']
            location = location.find('em').text
            locations.append((location, url))
        return locations

    def configuration(self, command: str, refresh: bool = False):
        """Set the location for which to display the weather"""

        locations = self.get_locations_accu(config.BROWSE_LOCATIONS[command],
                                            refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                print(f'{index + 1}) {location[0]}')
            selected_index = int(input('Please select location: '))
            location = locations[selected_index - 1]
            locations = self.get_locations_accu(location[1], refresh=refresh)

        self.save_configuration(command, *location)

    def get_weather_accu(self, page: str, refresh: bool = False) -> dict:
        """Return information collected from AccuWeather"""

        weather_page = BeautifulSoup(page, 'html.parser')
        current_day_selection = weather_page.find('li', {'class': ['day current first cl',
                                                                   'night current first cl']})

        weather_info = {}
        if current_day_selection:
            current_day_url = current_day_selection.find('a').attrs['href']
            if current_day_url:
                current_day_page = self.get_page_from_server(current_day_url,
                                                             refresh=refresh)
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

    def run(self, refresh=False):
        """Main run for provider"""
        content = self.get_page_from_server(self.url, refresh=refresh)
        return self.get_weather_accu(content, refresh=refresh)


class Rp5WeatherProvider:

    """Weather provider for Rp5Weather site.
    """

    def __init__(self, command=None):
        self.name = config.RP5_PROVIDER_NAME

        if command is not None:
            location, url = self.get_configuration(command)
            self.location = location
            self.url = url

    def get_configuration_file(self):
        """Path to the CONFIG_FILE.

        Returns path to configuration file in your home directory.
        """

        return Path.home() / config.CONFIG_FILE

    def save_configuration(self, command: str, name: str, url: str):
        """Write the location to the configfile"""

        parser = configparser.ConfigParser()
        parser[command] = {'name': name, 'url': url}
        with open(self.get_configuration_file(), 'w') as configfile:
            parser.write(configfile)

    def get_configuration(self, command: str) -> tuple:
        """Returns name of the city and related url"""

        name = config.DEFAULT_NAME
        url = config.DEFAULT_URL[command]

        parser = configparser.ConfigParser()
        parser.read(self.get_configuration_file())

        if command in parser.sections():
            configuration = parser[command]
            name, url = configuration['name'], configuration['url']

        return name, url

    def get_request_headers(self) -> dict:
        """Return information for headers"""

        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    def get_cache_directory(self):
        """Return path to the cache directory"""

        return Path.home() / config.CACHE_DIR

    def cache_is_valid(self, path) -> bool:
        """Check if current cache file is valid"""

        return (time.time() - path.stat().st_mtime) < config.CACHE_TIME

    def get_url_hash(self, url: str) -> str:
        """Generates hash for given url"""

        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def save_cache(self, url: str, page_source: str):
        """Save page source data to file"""

        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
        with (cache_dir / url_hash).open('wb') as cache_file:
            cache_file.write(page_source)

    def get_cache(self, url: str):
        """Return cache data if any exists"""

        cache = b''
        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            cache_path = cache_dir / url_hash
            if cache_path.exists() and self.cache_is_valid(cache_path):
                with cache_path.open('rb') as cache_file:
                    cache = cache_file.read()

        return cache

    def clear_app_cache(self):
        """Delete directory with cache"""

        cache_dir = self.get_cache_directory()
        shutil.rmtree(cache_dir)

    def delete_invalid_cache(self):
        """Delete all invalid (old) cache"""

        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            path = Path(cache_dir)
            dirs = os.listdir(path)
            for file in dirs:
                life_time = time.time() - (path / file).stat().st_mtime
                if life_time > config.DAY_IN_SECONDS:
                    os.remove(path / file)

    def get_page_from_server(self, page_url: str, refresh: bool = False) -> str:
        """Return information about the page in the string format"""

        cache = self.get_cache(page_url)
        if cache and not refresh:
            page = cache
        else:
            request = Request(page_url, headers=self.get_request_headers())
            page = urlopen(request).read()
            self.save_cache(page_url, page)

        return page.decode('utf-8')

    def get_locations_rp5(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls"""

        locations_page = self.get_page_from_server(locations_url, refresh=refresh)
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
        else:
            for location in places:
                url = location.find('b')
                url = url.find('a').attrs['href']
                url = f'http://rp5.ua{url}'
                location = location.find('b').text[:-1]
                locations.append((location, url))

        return locations

    def configuration(self, command: str, refresh: bool = False):
        """Set the location for which to display the weather"""

        locations = self.get_locations_rp5(config.BROWSE_LOCATIONS[command],
                                           refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                print(f'{index + 1}) {location[0]}')
            selected_index = int(input('Please select location: '))
            location = locations[selected_index - 1]
            locations = self.get_locations_rp5(location[1], refresh=refresh)

        self.save_configuration(command, *location)

    def get_weather_rp5(self, page: str) -> dict:
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

    def run(self, refresh=False):
        """Main run for provider"""
        content = self.get_page_from_server(self.url, refresh=refresh)
        return self.get_weather_rp5(content)
