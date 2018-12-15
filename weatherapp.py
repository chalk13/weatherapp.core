"""Weather application project.

Resources: AccuWeather, RP5
Packages: urllib
"""
import argparse
import csv
import html
import sys
from providers import AccuWeatherProvider
from providers import Rp5WeatherProvider

# TODO: weatherapp.ini must contain information from both sites
# TODO: add option for the config commands to erase specific site settings
# --reset-defaults
# TODO: add option which takes the num of sec on which to cache the site
# --cache-for
# TODO: add a command that shows the weather for tomorrow


def get_weather_info_to_save(command: str) -> dict:
    """Return information from weather site to save"""

    accu = AccuWeatherProvider(command)
    rp5 = Rp5WeatherProvider(command)

    if command == 'accu':
        _, content = get_city_name_page_content(command)
        weather_info = accu.get_weather_accu(content)
    if command == 'rp5':
        _, content = get_city_name_page_content(command)
        weather_info = rp5.get_weather_rp5(content)

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


def get_city_name_page_content(command: str, refresh: bool = False) -> tuple:
    """Return name of the city and page content"""

    accu = AccuWeatherProvider(command)
    rp5 = Rp5WeatherProvider(command)

    if command == 'accu':
        city_name, city_url = accu.get_configuration(command)
        content = accu.get_page_from_server(city_url, refresh=refresh)
    if command == 'rp5':
        city_name, city_url = rp5.get_configuration(command)
        content = rp5.get_page_from_server(city_url, refresh=refresh)

    return city_name, content


def get_weather_info(command: str, refresh: bool = False):
    """Function to get weather info"""

    accu = AccuWeatherProvider(command)
    rp5 = Rp5WeatherProvider(command)

    if command == 'accu':
        print(f'Information from {command.upper()} weather site:')
        program_output(accu.location, accu.run(refresh=refresh))
    if command == 'rp5':
        print(f'Information from {command.upper()} weather site:')
        program_output(rp5.location, rp5.run(refresh=refresh))


def main(argv):
    """Main entry point"""

    # Both AccuWeatherProvider and Rp5WeatherProvider classes have
    # the function clear_app_cache and delete_invalid_cache.
    # This will be fixed later.
    # That's why we can use each of them to clear cache.
    accu = AccuWeatherProvider()
    rp5 = Rp5WeatherProvider()

    accu.delete_invalid_cache()

    known_commands = {'accu': get_weather_info,
                      'rp5': get_weather_info,
                      'config': {'accu': accu.configuration,
                                 'rp5': rp5.configuration},
                      'save_to_csv': write_info_to_csv,
                      'clear-cache': accu.clear_app_cache}

    parser = argparse.ArgumentParser(description='Application information')
    parser.add_argument('command', help='Service name', nargs='*')
    parser.add_argument('--refresh', help='Update caches', action='store_true')
    params = parser.parse_args(argv)

    if params.command:
        command = params.command[0]
        weather_site = params.command[0]
        if len(params.command) == 2:
            command = params.command[0]
            weather_site = params.command[1]
        if command == 'clear-cache':
            known_commands[command]()
        elif command == 'save_to_csv':
            known_commands[command](weather_site)
        elif command in ('accu', 'rp5'):
            known_commands[command](weather_site,
                                    refresh=params.refresh)
        elif command == 'config':
            known_commands[command][weather_site](weather_site,
                                                  refresh=params.refresh)
        else:
            print('Unknown command provided.')
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
