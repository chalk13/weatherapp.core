"""Weather application project.

Resources: AccuWeather, RP5
Packages: urllib
"""
import argparse
import csv
import html
import sys
from providers import AccuWeatherProvider

# TODO: weatherapp.ini must contain information from both sites
# TODO: add option for the config commands to erase specific site settings
# --reset-defaults
# TODO: add option which takes the num of sec on which to cache the site
# --cache-for
# TODO: add a command that shows the weather for tomorrow


'''def get_locations_rp5(locations_url: str, refresh: bool = False) -> list:
    """Return a list of locations and related urls"""

    locations_page = get_page_from_server(locations_url, refresh=refresh)
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


def get_weather_rp5(page: str) -> dict:
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

    return weather_info'''


'''def get_weather_info_to_save(command: str) -> dict:
    """Return information from weather site to save"""

    if command == 'accu':
        city_name, content = get_city_name_page_content(command)
        weather_info = get_weather_accu(content)
    if command == 'rp5':
        city_name, content = get_city_name_page_content(command)
        weather_info = get_weather_rp5(content)

    return weather_info'''


'''def write_info_to_csv(command: str):
    """Write data to a CSV file"""

    info = get_weather_info_to_save(command)

    output_file = open('weather_data.csv', 'w', newline='')
    output_writer = csv.writer(output_file)
    output_writer.writerow(['Parameters', 'Description'])
    for key, value in info.items():
        output_writer.writerow([key, value])
    output_file.close()'''


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


'''def get_city_name_page_content(command: str, refresh: bool = False) -> tuple:
    """Return name of the city and page content"""

    city_name, city_url = get_configuration(command)
    content = get_page_from_server(city_url, refresh=refresh)
    return city_name, content'''


def get_weather_info(command: str, refresh: bool = False):
    """Function to get weather info"""

    accu = AccuWeatherProvider()

    if command == 'accu':
        print(f'Information from {command.upper()} weather site:')
        program_output(accu.location, accu.run(refresh=refresh))
#    if command == 'rp5':
#        print(f'Information from {command.upper()} weather site:')
#        program_output(city_name, get_weather_rp5(content))


def main(argv):
    """Main entry point"""

#    delete_invalid_cache()

    known_commands = {'accu': get_weather_info,
                      'rp5': get_weather_info}
#                      'config': configuration,
#                      'save_to_csv': write_info_to_csv,
#                      'clear-cache': clear_app_cache}

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
        elif command in known_commands:
            known_commands[command](weather_site,
                                    refresh=params.refresh)
        else:
            print('Unknown command provided.')
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
