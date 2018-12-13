"""Weather providers for the weather application project.

This file includes classes for each weather service provider.
Providers: accuweather.com, rp5.ua
"""

import configparser
from pathlib import Path

import config


class AccuWeatherProvider:

    """Weather provider for AccuWeather site.
    """

    def __init__(self):
        self.name = config.ACCU_PROVIDER_NAME

        location, url = self.get_configuration()
        self.location = location
        self.url = url

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

    def get_configuration_file(self):
        """Path to the CONFIG_FILE.

        Returns path to configuration file in your home directory.
        """

        return Path.home() / config.CONFIG_FILE
