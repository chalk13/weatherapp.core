"""Abstract manager class for the weather application."""

import abc


class Manager(abc.ABC):
    """Abstract class for project commands managers."""

    @abc.abstractmethod
    def add(self, name, command):
        """Add new command to manager.

        :param name: command name
        :type name: str
        :param command: command class
        :type command: Sub type of `weatherapp.core.abstract.Command`
        """

    @abc.abstractmethod
    def get(self, name):
        """Get command from manager by name.

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __getitem__(self, name):
        """Get item by name.

        Implementation of this 'dunder' method allow us to access
        commands by name (the same as it works in dictionaries).

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __contains__(self, name):
        """Check if command with provided name is in manager.

        Implementation of this 'dunder' method allow us to use 'in'
        operator with manager to check if command exists in manager.

        :param name: command name
        :type name: str
        """
