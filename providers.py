import config


class AccuWeatherProvider:

    """Weather provider for AccuWeather site.
    """

    def __init__(self):
        self.name = config.ACCU_PROVIDER_NAME
        self.location = ''
        self.url = ''

    def get_configuration(command: str) -> tuple:
        """Returns name of the city and related url"""

        name = DEFAULT_NAME
        url = DEFAULT_URL[command]

        parser = configparser.ConfigParser()
        parser.read(get_configuration_file())

        if command in parser.sections():
            config = parser[command]
            name, url = config['name'], config['url']

        return name, url