"""Main module of the application"""

import csv
import html
import os
import sys
import shutil
import time
from argparse import ArgumentParser
from pathlib import Path

from providermanager import ProviderManager

import config


class Providers:
    """Prints all available providers"""

    def __init__(self):
        self.providers = ProviderManager()

    def all_providers(self):
        print(f"Available providers:")
        for number, provider in enumerate(self.providers._providers.values(), 1):
            print(f'{number}. {provider.title}')


class Config:
    """Customizes the location for the weather site."""

    def __init__(self, weather_site):
        self.weather_site = weather_site
        self.providermanager = ProviderManager()

    def customizes(self, weather_site: str):
        provider = self.providermanager[weather_site]
        provider_obj = provider(self)
        provider_obj.configuration(weather_site)


class App:
    """Weather aggregator application"""

    def __init__(self):
        self.arg_parser = self._arg_parse()
        self.providermanager = ProviderManager()
        self.providers = Providers()

    def _arg_parse(self):
        """Initialize argument parser."""
        arg_parser = ArgumentParser(description='Application information',
                                    add_help=False)
        arg_parser.add_argument('command', help='Command', nargs='?')
        arg_parser.add_argument('--refresh', help='Bypass caches',
                                action='store_true')

        return arg_parser

    def get_cache_directory(self):
        """Return path to the cache directory"""

        return Path.home() / config.CACHE_DIR

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

    def get_weather_info_to_save(self, weather_site: str) -> dict:
        """Return information from weather site to save"""

        if weather_site in self.providermanager:
            provider = self.providermanager[weather_site]
            provider_obj = provider(self)
            if weather_site == 'accu':
                _, content = self.get_city_name_page_content(weather_site)
                weather_info = provider_obj.get_weather_accu(content)
            if weather_site == 'rp5':
                _, content = self.get_city_name_page_content(weather_site)
                weather_info = provider_obj.get_weather_rp5(content)

        return weather_info

    def write_info_to_csv(self, weather_site: str):
        """Write data to a CSV file"""

        info = self.get_weather_info_to_save(weather_site)

        with open('weather_data.csv', 'w', newline='') as output_file:
            field_names = ['Parameters', 'Description']
            writer = csv.DictWriter(output_file, fieldnames=field_names)
            writer.writeheader()
            for key, value in info.items():
                writer.writerow({'Parameters': key, 'Description': value})

    def get_city_name_page_content(self, weather_site: str, refresh: bool = False) -> tuple:
        """Return name of the city and page content"""

        if weather_site in self.providermanager:
            provider = self.providermanager[weather_site]
            provider_obj = provider(self)
            if weather_site == 'accu':
                city_name, city_url = provider_obj.get_configuration()
                content = provider_obj.get_page_from_server(city_url, refresh=refresh)
            if weather_site == 'rp5':
                city_name, city_url = provider_obj.get_configuration()
                content = provider_obj.get_page_from_server(city_url, refresh=refresh)

        return city_name, content

    def program_output(self, title: str, city: str, info: dict):
        """Print the application output in readable form"""

        length_column_1 = max(len(key) for key in info.keys())
        length_column_2 = max(len(value) for value in info.values())

        print(f'{title}')
        print('-'*len(title))
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

    def run(self, argv):
        """Run application

        :param argv: list of passed arguments
        """

        self.delete_invalid_cache()

        self.options, remaining_args = self.arg_parser.parse_known_args(argv)
        command_name = self.options.command
        if remaining_args:
            weather_site = remaining_args[0]

        if command_name == 'providers':
            self.providers.all_providers()
        elif command_name == 'clear-cache':
            self.clear_app_cache()
        elif command_name == 'save-to-csv':
            self.write_info_to_csv(weather_site)
        elif command_name == 'config':
            site_configuration = Config(weather_site)
            site_configuration.customizes(weather_site)
        elif not command_name:
            # run all weather providers by default
            for provider in self.providermanager._providers.values():
                provider_obj = provider(self)
                self.program_output(provider_obj.title,
                                    provider_obj.location,
                                    provider_obj.run())
        elif command_name in self.providermanager:
            # run specific provider
            provider = self.providermanager[command_name]
            provider_obj = provider(self)
            self.program_output(provider_obj.title,
                                provider_obj.location,
                                provider_obj.run())
        else:
            print('Unknown command provided.')
            sys.exit(1)


def main(argv=sys.argv[1:]):
    """Main entry point"""

    return App().run(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
