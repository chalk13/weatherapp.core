"""Weather providers for the weather application project.

This file includes classes for each weather service provider.
Providers: accuweather.com, rp5.ua
"""

from bs4 import BeautifulSoup

import config
from abstract import WeatherProvider


class AccuWeatherProvider(WeatherProvider):

    """Weather provider for AccuWeather site.
    """

    name = config.ACCU_PROVIDER_NAME
    title = config.ACCU_PROVIDER_TITLE

    def get_default_location(self):
        """Default location name."""
        return config.DEFAULT_NAME

    def get_default_url(self):
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
                    print()
                print(f'{index + 1}) {location[0]}', end=' ')
            print()
            selected_index = int(input('Please select location: '))
            location = locations[selected_index - 1]
            locations = self.get_locations_accu(location[1], refresh=refresh)

        self.save_configuration(*location)

    def get_weather_info(self, page: str, refresh: bool = False) -> dict:
        """Return information collected from AccuWeather."""

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


class Rp5WeatherProvider(WeatherProvider):

    """Weather provider for Rp5Weather site.
    """

    name = config.RP5_PROVIDER_NAME
    title = config.RP5_PROVIDER_TITLE

    def get_default_location(self):
        """Default location name."""
        return config.DEFAULT_NAME

    def get_default_url(self):
        """Default location url."""
        return config.DEFAULT_URL_RP5

    def get_locations_rp5(self, locations_url: str, refresh: bool = False) -> list:
        """Return a list of locations and related urls."""

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
        """Set the location for which to display the weather."""

        locations = self.get_locations_rp5(config.BROWSE_LOCATIONS[command],
                                           refresh=refresh)

        while locations:
            for index, location in enumerate(locations):
                if index % 5 == 0:
                    print()
                print(f'{index + 1}) {location[0]}', end=' ')
            print()
            selected_index = int(input('Please select location: '))
            location = locations[selected_index - 1]
            locations = self.get_locations_rp5(location[1], refresh=refresh)

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
