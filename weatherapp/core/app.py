"""Main module of the application."""

import csv
import os
import sys
import shutil
import time
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

from loguru import logger

from weatherapp.core.formatters import TableFormatter
from weatherapp.core.providermanager import ProviderManager
from weatherapp.core.commandmanager import CommandManager
from weatherapp.core import config


class App:
    """Weather aggregator application."""

    def __init__(self, stdin=None, stdout=None, stderr=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.arg_parser = self._arg_parse()
        self.providermanager = ProviderManager()
        self.commandmanager = CommandManager()
        self.formatters = self._load_formatters()

    @staticmethod
    def _arg_parse():
        """Initialize argument parser."""
        arg_parser = ArgumentParser(description='Application information',
                                    add_help=False)
        arg_parser.add_argument('command', help='Command', nargs='?')
        arg_parser.add_argument('--refresh',
                                help='Bypass caches',
                                action='store_true')
        arg_parser.add_argument('--debug',
                                help='Info for developer',
                                action='store_true',
                                default=False)
        arg_parser.add_argument('-f', '--formatter',
                                help='Output format, defaults to table',
                                action='store',
                                default='table')

        return arg_parser

    @staticmethod
    def configure_logging(fname='weatheapp'):
        """Set up logging for any log output."""

        logger.add(f'{fname}_{{time:MM:DD}}.log', retention='5 days')

    @staticmethod
    def get_cache_directory():
        """Return path to the cache directory."""

        return Path.home() / config.CACHE_DIR

    def clear_app_cache(self):
        """Delete directory with cache."""

        cache_dir = self.get_cache_directory()

        try:
            shutil.rmtree(cache_dir)
        except FileNotFoundError:
            msg = 'The cache directory is empty or not found'
            if self.options.debug:
                logger.exception(msg)
            else:
                logger.error(msg)

    def delete_invalid_cache(self):
        """Delete all invalid (old) cache.

        The time during which the cache is valid
        can be changed in config.py
        """

        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            path = Path(cache_dir)
            dirs = os.listdir(path)
            for file in dirs:
                life_time = time.time() - (path / file).stat().st_mtime
                if life_time > config.DAY_IN_SECONDS:
                    os.remove(path / file)

    def get_weather_info_to_save(self, weather_site: str) -> dict:
        """Return information from weather site to save."""

        if weather_site in self.providermanager:
            provider = self.providermanager[weather_site]
            provider_obj = provider(self)
            _, content = self.get_city_name_page_content(weather_site)
            weather_info = provider_obj.get_weather_info(content)

        return weather_info

    def write_info_to_csv(self, weather_site: str):
        """Write data to a CSV file."""

        info = self.get_weather_info_to_save(weather_site)

        with open('weather_data.csv', 'w', newline='') as output_file:
            field_names = ['Parameters', 'Description']
            writer = csv.DictWriter(output_file, fieldnames=field_names)
            writer.writeheader()
            for key, value in info.items():
                writer.writerow({'Parameters': key, 'Description': value})

    def get_city_name_page_content(self, weather_site: str, refresh: bool = False):
        """Return name of the city and page content."""

        PlaceInfo = namedtuple('PlaceInfo', 'place_name page_content')

        if weather_site in self.providermanager:
            provider = self.providermanager[weather_site]
            provider_obj = provider(self)
            city_name, city_url = provider_obj.get_configuration()
            content = provider_obj.get_page_from_server(city_url, refresh=refresh)
            place_info = PlaceInfo(city_name, content)

        return place_info

    @staticmethod
    def _load_formatters():
        return {'table': TableFormatter}

    def program_output(self, title: str, city: str, info: dict):
        """Print the application output in readable form."""

        formatter = self.formatters.get(self.options.formatter, 'table')()
        columns = [title, city]

        self.stdout.write(formatter.emit(columns, info))
        self.stdout.write('\n')

    def run_command(self, name, argv):
        """Run command"""

        command = self.commandmanager.get(name)
        try:
            command(self).run(argv)
        except Exception:
            msg = f'Error during command: {name} run'
            if self.options.debug:
                logger.exception(msg)
            else:
                logger.error(msg)

    def run_provider(self, name, argv):
        """Run specified provider."""

        provider = self.providermanager.get(name)
        if provider:
            provider = provider(self)
            self.program_output(provider.title,
                                provider.location,
                                provider.run(argv))

    def run_providers(self, argv):
        """Execute all available providers."""

        for _, provider in self.providermanager:
            provider = provider(self)
            self.program_output(provider.title,
                                provider.location,
                                provider.run(argv))

    def run(self, argv):
        """Run application.

        :param argv: list of passed arguments
        """

        self.delete_invalid_cache()

        self.options, remaining_args = self.arg_parser.parse_known_args(argv)
        self.configure_logging()
        logger.debug(f'Got the following args: {argv}')
        command_name = self.options.command

        if not command_name:
            # run all providers
            return self.run_providers(remaining_args)

        if command_name in self.commandmanager:
            return self.run_command(command_name, remaining_args)

        if command_name in self.providermanager:
            return self.run_provider(command_name, remaining_args)

        if remaining_args:
            weather_site = remaining_args[0]

        if command_name == 'clear-cache':
            self.clear_app_cache()
        elif command_name == 'save-to-csv':
            self.write_info_to_csv(weather_site)
        else:
            self.stdout.write('Unknown command provided. \n')
            sys.exit(1)


def main(argv=sys.argv[1:]):
    """Main entry point."""

    return App().run(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
