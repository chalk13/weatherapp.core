"""Main module of the application."""

import csv
import html
import logging
import os
import sys
import shutil
import time
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

from providermanager import ProviderManager
from commandmanager import CommandManager
import config


class App:
    """Weather aggregator application."""

    logger = logging.getLogger(__name__)
    LOG_LEVEL_MAP = {0: logging.WARNING,
                     1: logging.INFO,
                     2: logging.DEBUG}

    def __init__(self):
        self.arg_parser = self._arg_parse()
        self.providermanager = ProviderManager()
        self.commandmanager = CommandManager()

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
                                action='store_true')
        arg_parser.add_argument('-v', '--verbose',
                                help='Increase verbosity of output',
                                action='count',
                                dest='verbose_level',
                                default=config.DEFAULT_VERBOSE_LEVEL)

        return arg_parser

    def configure_logging(self):
        """Create logging handlers for any log output."""

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        console = logging.StreamHandler()
        console_level = self.LOG_LEVEL_MAP.get(self.options.verbose_level,
                                               logging.WARNING)
        console.setLevel(console_level)
        formatter = logging.Formatter(config.DEFAULT_MESSAGE_FORMAT,
                                      '%Y-%m-%d %H:%M:%S %p')
        console.setFormatter(formatter)
        root_logger.addHandler(console)

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
            msg = 'The cache directory is empty or not found.'
            if self.options.debug:
                self.logger.exception(msg)
            else:
                self.logger.error(msg)

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
    def program_output(title: str, city: str, info: dict):
        """Print the application output in readable form."""

        length_column_1 = max(len(key) for key in info.keys())
        length_column_2 = max(len(value) for value in info.values())

        print(f'{title}')
        print('-'*len(title))
        print(f'{city.upper()}')

        def border_line(column_1: int, column_2: int) -> str:
            """Print a line for dividing information."""

            line = ''.join(['+'] + ['-' * (column_1 + column_2 + 5)] + ['+'])
            return line

        def status_msg(msg: str, state: str) -> str:
            """Print weather information."""

            result = f"| {msg} {' ' * (length_column_1 - len(msg))}" \
                     f"| {state} {' ' * (length_column_2 - len(state))}|\n"
            return result

        print(border_line(length_column_1, length_column_2))

        for key, value in info.items():
            print(status_msg(key, html.unescape(value)), end='')

        print(border_line(length_column_1, length_column_2))

    def run(self, argv):
        """Run application.

        :param argv: list of passed arguments
        """

        self.delete_invalid_cache()

        self.options, remaining_args = self.arg_parser.parse_known_args(argv)
        self.configure_logging()
        self.logger.debug('Got the following args: %s', argv)
        command_name = self.options.command

        if remaining_args:
            weather_site = remaining_args[0]

        if command_name == 'clear-cache':
            self.clear_app_cache()
        elif command_name == 'save-to-csv':
            self.write_info_to_csv(weather_site)

        elif command_name in self.commandmanager:
            command_factory = self.commandmanager.get(command_name)
            try:
                command_factory(self).run(remaining_args)
            except Exception:
                msg = 'Error during command: %s run'
                if self.options.debug:
                    self.logger.exception(msg, command_name)
                else:
                    self.logger.error(msg, command_name)

        elif not command_name:
            # run all weather providers by default
            for provider in self.providermanager._providers.values():
                self.program_output(provider.title,
                                    provider(self).location,
                                    provider(self).run(remaining_args))
        elif command_name in self.providermanager:
            # run specific provider
            provider = self.providermanager[command_name]
            self.program_output(provider.title,
                                provider(self).location,
                                provider(self).run(remaining_args))
        else:
            print('Unknown command provided.')
            sys.exit(1)


def main(argv=sys.argv[1:]):
    """Main entry point."""

    return App().run(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
