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

from bs4 import BeautifulSoup

import config


class AccuWeatherProvider:

    """Weather provider for AccuWeather site.
    """

    def __init__(self):
        self.name = config.ACCU_PROVIDER_NAME

        location, url = self.get_configuration()
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
