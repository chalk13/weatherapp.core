"""Weather application project.

Resources: AccuWeather, RP5, Sinoptik
Packages: urllib
"""
import argparse
import html
import sys
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


def get_request_headers():
    """Return information for headers"""

    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'}


def get_page_from_server(page_url: str) -> str:  # getting page from server
    """Return information about the page in the string format"""

    request = Request(page_url, headers=get_request_headers())
    page = urlopen(request).read()

    return page.decode('utf-8')


def get_weather_info(page):
    """Return information collected from tags"""

    weather_page = BeautifulSoup(page, 'html.parser')
    current_day_selection = weather_page.find('li', class_='night current first cl')

    weather_info = {}
    if current_day_selection:
        current_day_url = current_day_selection.find('a').attrs['href']
        if current_day_url:
            current_day_page = get_page_from_server(current_day_url)
            if current_day_page:
                current_day = BeautifulSoup(current_day_page, 'html.parser')
                weather_details = current_day.find('div', attrs={'id': 'detail-now'})
                condition = weather_details.find('span', class_='cond')
                if condition:
                    weather_info['Condition'] = condition.text
                temp = weather_details.find('span', class_='large-temp')
                if temp:
                    weather_info['Temperature'] = temp.text
                feal_temp = weather_details.find('span', class_='small-temp')
                if feal_temp:
                    weather_info['RealFeel'] = feal_temp.text
                wind_info = weather_details.find_all('li', class_='wind')
                if wind_info:
                    weather_info['Wind'] = ' '.join(map(lambda t: t.text.strip(), wind_info))

    return weather_info


def program_output(info):
    """Print the application output in readable form"""

    length_column_1 = max(len(key) for key in info.keys())
    length_column_2 = max(len(value) for value in info.values())

    def border_line(column_1, column_2):
        """Print a line for dividing information"""

        line = ''.join(['+'] + ['-' * (column_1 + column_2 + 5)] + ['+'])
        return line

    def status_msg(msg, state):
        """Print weather information"""

        result = "| " + msg + (' ' * (length_column_1 - len(msg))) + \
                 " | " + state + (' ' * (length_column_2 - len(state))) + " |" + '\n'
        return result

    print(border_line(length_column_1, length_column_2))

    for key, value in info.items():
        print(status_msg(key, value), end='')

    print(border_line(length_column_1, length_column_2))


def main(argv):
    """Main entry point"""

    known_commands = {'accu': 'AccuWeather', 'rp5': 'RP5', 'sin': 'Sinoptik'}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to choose weather website', nargs=1)
    params = parser.parse_args(argv)

    weather_sites = {'AccuWeather': ACU_URL,
                     'RP5': RP5_URL,
                     'Sinoptik': SIN_URL}

    if params.command:
        command = params.command[0]
        if command in known_commands:
            weather_sites = {known_commands[command]: weather_sites[known_commands[command]]}
        else:
            print('Unknown command provided.')
            sys.exit(1)

    for site in weather_sites:
        url = weather_sites[site]
        content = get_page_from_server(url)
        program_output(get_weather_info(content))


# start pages for getting information
ACU_URL = 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505'
RP5_URL = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'
SIN_URL = 'https://ua.sinoptik.ua'


if __name__ == '__main__':
    main(sys.argv[1:])
