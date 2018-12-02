"""Weather application project.

Resources: AccuWeather, RP5
Packages: urllib
"""
import argparse
import csv
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


def get_weather_accu(page):
    """Return information collected from AccuWeather"""

    weather_page = BeautifulSoup(page, 'html.parser')
    current_day_selection = weather_page.find('li', {'class': ['day current first cl', 'night current first cl']})

    weather_info = {}
    if current_day_selection:
        current_day_url = current_day_selection.find('a').attrs['href']
        if current_day_url:
            current_day_page = get_page_from_server(current_day_url)
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


def get_weather_rp5(page):
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

    return weather_info


def write_info_to_csv(info: dict):
    """Write data to a CSV file"""

    output_file = open('weather_data.csv', 'w', newline='')
    output_writer = csv.writer(output_file)
    output_writer.writerow(['Parameters', 'Description'])
    for key, value in info.items():
        output_writer.writerow([key, value])
    output_file.close()


def program_output(info: dict):
    """Print the application output in readable form"""

    length_column_1 = max(len(key) for key in info.keys())
    length_column_2 = max(len(value) for value in info.values())

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


def main(argv):
    """Main entry point"""

    known_commands = {'accu': 'AccuWeather',
                      'rp5': 'RP5'}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to choose weather website', nargs=1)
    params = parser.parse_args(argv)

    weather_sites = {'AccuWeather': ACU_URL, 'RP5': RP5_URL}

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
        if site == 'AccuWeather':
            program_output(get_weather_accu(content))
            write_info_to_csv(get_weather_accu(content))
        elif site == 'RP5':
            program_output(get_weather_rp5(content))
            write_info_to_csv(get_weather_rp5(content))


# start pages for getting information
ACU_URL = 'https://www.accuweather.com/en/ua/kyiv/324505/weather-forecast/324505'
RP5_URL = 'http://rp5.ua/Weather_in_Kiev,_Kyiv'


if __name__ == '__main__':
    main(sys.argv[1:])
