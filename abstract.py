"""Abstract classes for the weather application."""

import abc
import argparse


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

    @abc.abstractmethod
    def configurate(self):
        """Performs provider configuration."""

    @abc.abstractmethod
    def get_weather_info(self, content):
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
