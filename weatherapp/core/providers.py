"""Weather providers for the weather application project.

This file includes classes for each weather service provider.
Providers: accuweather.com, rp5.ua, sinoptik.ua
"""

from bs4 import BeautifulSoup
from loguru import logger

from weatherapp.core import config
from weatherapp.core.abstract import WeatherProvider


class AccuWeatherProvider(WeatherProvider):

    """Weather provider for AccuWeather site.
    """

    name = config.ACCU_PROVIDER_NAME
    title = config.ACCU_PROVIDER_TITLE

    @staticmethod
    def get_default_location():
        """Default location name."""
        return config.DEFAULT_NAME

    @staticmethod
    def get_default_url():
        """Default location url."""
        return config.DEFAULT_URL_ACCU

    def get_locations_accu(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls."""

        locations_page = self.get_page_from_server(locations_url, refresh=refresh)
        soup = BeautifulSoup(locations_page, 'html.parser')

        locations = []
        for location in soup.find_all('li', class_='drilldown cl'):
            url = location.find('a').attrs['href']
            location = location.find('em').text
            locations.append((location, url))
        return locations

    def configuration(self, command: str, refresh: bool = False):
        """Set the location for which to display the weather."""

        locations = self.get_locations_accu(config.BROWSE_LOCATIONS[command],
                                            refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                if index % 5 == 0:
                    self.stdout.write('\n')
                self.stdout.write(f'{index + 1}) {location[0]} ')
            self.stdout.write('\n')
            try:
                selected_index = int(input('Please select location: '))
                location = locations[selected_index - 1]
                locations = self.get_locations_accu(location[1], refresh=refresh)
            except IndexError:
                msg = 'The user enter too big number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)
            except ValueError:
                msg = 'The user did not enter an integer number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)

        self.save_configuration(*location)

    def get_weather_info(self, page: str, refresh: bool = False) -> dict:
        """Return information collected from AccuWeather."""

        weather_page = BeautifulSoup(page, 'html.parser')
        current_day_selection = weather_page.find_all('a', class_='current')

        weather_info = {}
        if current_day_selection:
            current_day_url = current_day_selection[0].get('href')
            current_day_url = f'https://www.accuweather.com/{current_day_url}'
            if current_day_url:
                current_day_page = self.get_page_from_server(current_day_url,
                                                             refresh=refresh)
                if current_day_page:
                    current_day = BeautifulSoup(current_day_page, 'html.parser')
                    temp = current_day.find('div', class_='temperatures')
                    curr_temp = temp.find('p', class_='value')
                    if curr_temp:
                        weather_info['Temperature'] = curr_temp.text.strip()
                    condition = current_day.find('div', class_='phrase')
                    if condition:
                        weather_info['Condition'] = condition.text
                    feel_temp = temp.find('p', class_='realFeel top')
                    if feel_temp:
                        curr_feel_temp = ''.join(i for i in feel_temp.text if i.isdigit())
                        if '-' in curr_feel_temp:
                            weather_info['RealFeel'] = f'-{curr_feel_temp}°'
                        else:
                            weather_info['RealFeel'] = f'{curr_feel_temp}°'

        return weather_info


class Rp5WeatherProvider(WeatherProvider):

    """Weather provider for Rp5 weather site.
    """

    name = config.RP5_PROVIDER_NAME
    title = config.RP5_PROVIDER_TITLE

    @staticmethod
    def get_default_location():
        """Default location name."""
        return config.DEFAULT_NAME

    @staticmethod
    def get_default_url():
        """Default location url."""
        return config.DEFAULT_URL_RP5

    def get_locations_rp5(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls."""

        locations_page = self.get_page_from_server(locations_url, refresh=refresh)
        soup = BeautifulSoup(locations_page, 'html.parser')

        locations = []
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
        """Set the location for which to display the weather."""

        locations = self.get_locations_rp5(config.BROWSE_LOCATIONS[command],
                                           refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                if index % 5 == 0:
                    self.stdout.write('\n')
                self.stdout.write(f'{index + 1}) {location[0]} ')
            self.stdout.write('\n')
            try:
                selected_index = int(input('Please select location: '))
                location = locations[selected_index - 1]
                locations = self.get_locations_rp5(location[1], refresh=refresh)
            except IndexError:
                msg = 'The user entered too big number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)
            except ValueError:
                msg = 'The user did not enter an integer number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)

        self.save_configuration(*location)

    @staticmethod
    def get_weather_info(page: str) -> dict:
        """Return information collected from RP5."""

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


class SinoptikWeatherProvider(WeatherProvider):

    """Weather provider for Sinoptik weather site.
    """

    name = config.SINOPTIK_PROVIDER_NAME
    title = config.SINOPTIK_PROVIDER_TITLE

    @staticmethod
    def get_default_location():
        """Default location name."""
        return config.DEFAULT_NAME

    @staticmethod
    def get_default_url():
        """Default location url."""
        return config.DEFAULT_URL_SINOPTIK

    def get_locations_sinoptik(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls."""

        locations_page = self.get_page_from_server(locations_url, refresh=refresh)
        soup = BeautifulSoup(locations_page, 'html.parser')

        locations = []
        places = soup.find('div', class_='mapRightCol')
        if places:
            for place in places.find_all('a'):
                location = place.text
                url = place.attrs['href']
                url = f'https:{url}'
                locations.append((location, url))

        return locations

    def configuration(self, command: str, refresh: bool = False):
        """Set the location for which to display the weather."""

        locations = self.get_locations_sinoptik(f'{config.BROWSE_LOCATIONS[command]}',
                                                refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                if index % 5 == 0:
                    self.stdout.write('\n')
                self.stdout.write(f'{index + 1}) {location[0]} ')
            self.stdout.write('\n')
            try:
                selected_index = int(input('Please select location: '))
                location = locations[selected_index - 1]
                locations = self.get_locations_sinoptik(location[1], refresh=refresh)
            except IndexError:
                msg = 'The user entered too big number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)
            except ValueError:
                msg = 'The user did not enter an integer number'
                if self.app.options.debug:
                    logger.exception(msg)
                else:
                    logger.error(msg)

        self.save_configuration(*location)

    @staticmethod
    def get_weather_info(page: str) -> dict:
        """Return information collected from SINOPTIK."""

        weather_page = BeautifulSoup(page, 'html.parser')
        current_day_weather = weather_page.find('div', class_='imgBlock')
        current_day_temperature = weather_page.find('div', class_='main loaded')

        weather_info = {}
        if current_day_weather:
            temperature = current_day_weather.find('p', class_='today-temp')
            if temperature:
                weather_info['Temperature'] = temperature.text
        if current_day_weather:
            condition = current_day_weather.find('img', alt=True)
            if condition:
                weather_info['Condition'] = condition['alt']
        if current_day_temperature:
            min_temp = current_day_temperature.find('div', class_='min')
            max_temp = current_day_temperature.find('div', class_='max')
            weather_info['Expect'] = f'{min_temp.text}... {max_temp.text}'

        return weather_info
