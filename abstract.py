"""Abstract classes for the weather application."""

import abc
import argparse
import configparser
import hashlib
import time
from collections import namedtuple
from pathlib import Path

import requests

import config


class Command(abc.ABC):
    """Base class for commands.

    :param app: Main application instance
    :type app: `app.App`
    """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def get_argument_parser():
        """Initialize argument parser for command."""

        parser = argparse.ArgumentParser()
        return parser

    @abc.abstractmethod
    def run(self, argv):
        """Invoked by application when the command is run.

        Should be overridden in subclass.
        """


class WeatherProvider(Command):
    """Weather provider abstract class.

    Defines behavior for all weather providers.
    """

    def __init__(self, app):
        super().__init__(app)

        location, url = self.get_configuration()
        self.location = location
        self.url = url

    @abc.abstractmethod
    def get_default_location(self):
        """Default location name."""

    @abc.abstractmethod
    def get_default_url(self):
        """Default location url."""

    @abc.abstractmethod
    def configuration(self):
        """Performs provider configuration."""

    @abc.abstractmethod
    def get_weather_info(self, content: str):
        """Collects weather information.

        Gets weather information from source and produce it in
        the following format.

        weather_info = {
            temp: ''  # temperature
            condition: ''  # weather condition
            feel_temp: ''  # feels like temperature
            wind_info: ''  # information about wind
        }
        """

    def get_name(self):
        """Return provider name."""
        return self.name

    @staticmethod
    def get_configuration_file():
        """Path to the CONFIG_FILE.

        Returns path to configuration file in your home directory.
        """

        return Path.home() / config.CONFIG_FILE

    def save_configuration(self, name: str, url: str):
        """Write the location to the configfile."""

        parser = configparser.ConfigParser()
        config_file = self.get_configuration_file()

        if config_file.exists():
            parser.read(config_file)

        parser[self.get_name()] = {'name': name, 'url': url}
        with open(config_file, 'w') as configfile:
            parser.write(configfile)

    def get_configuration(self):
        """Returns name of the city and related url."""

        Place = namedtuple('Place', 'place_name place_url')

        try:
            name = self.get_default_location()
            url = self.get_default_url()
            place_info = Place(name, url)
        except AttributeError:
            msg = 'Error while receiving location configuration'
            if self.app.options.debug:
                self.app.logger.exception(msg)
            else:
                self.app.logger.error(msg)

        parser = configparser.ConfigParser()

        try:
            parser.read(self.get_configuration_file())
        except configparser.Error:
            msg = f'Bad configuration file.' \
                  f'Please change configuration for provider:' \
                  f'{self.get_name()}'
            if self.app.options.debug:
                self.app.logger.exception(msg)
            else:
                self.app.logger.error(msg)

        if self.get_name() in parser.sections():
            location_config = parser[self.get_name()]
            name, url = location_config['name'], location_config['url']
            place_info = Place(name, url)

        return place_info

    @staticmethod
    def get_request_headers() -> dict:
        """Return information for headers."""

        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    @staticmethod
    def get_cache_directory():
        """Return path to the cache directory."""

        return Path.home() / config.CACHE_DIR

    @staticmethod
    def cache_is_valid(path) -> bool:
        """Check if current cache file is valid."""

        return (time.time() - path.stat().st_mtime) < config.CACHE_TIME

    @staticmethod
    def get_url_hash(url: str) -> str:
        """Generates hash for given url."""

        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def save_cache(self, url: str, page_source: str):
        """Save page source data to file."""

        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
        with (cache_dir / url_hash).open('wb') as cache_file:
            cache_file.write(page_source)

    def get_cache(self, url: str) -> bytes:
        """Return cache data if any exists."""

        cache = b''
        url_hash = self.get_url_hash(url)
        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            cache_path = cache_dir / url_hash
            if cache_path.exists() and self.cache_is_valid(cache_path):
                with cache_path.open('rb') as cache_file:
                    cache = cache_file.read()

        return cache

    def get_page_from_server(self, page_url: str, refresh: bool = False) -> str:
        """Return information about the page in the string format."""

        cache = self.get_cache(page_url)
        if cache and not refresh:
            page_source = cache
        else:
            page = requests.get(page_url, headers=self.get_request_headers())
            page_source = page.content
            self.save_cache(page_url, page_source)

        return page_source.decode('utf-8')

    def run(self, refresh=False):
        """Main run for provider."""
        content = self.get_page_from_server(self.url, refresh=refresh)
        return self.get_weather_info(content)


class Manager(abc.ABC):
    """Abstract class for project commands managers."""

    @abc.abstractmethod
    def add(self, name, command):
        """Add new command to manager.

        :param name: command name
        :type name: str
        :param command: command class
        :type command: Sub type of `weatherapp.abstract.Command`
        """

    @abc.abstractmethod
    def get(self, name):
        """Get command from manager by name.

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __getitem__(self, name):
        """Get item by name.

        Implementation of this 'dunder' method allow us to access
        commands by name (the same as it works in dictionaries).

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __contains__(self, name):
        """Check if command with provided name is in manager.

        Implementation of this 'dunder' method allow us to use 'in'
        operator with manager to check if command exists in manager.

        :param name: command name
        :type name: str
        """
