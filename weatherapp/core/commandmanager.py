"""Manager for the weather application commands."""

from weatherapp.core.commands import Configure, Providers
from weatherapp.core.abstract import Manager


class CommandManager(Manager):
    """Manager for app commands."""

    def __init__(self):
        self._commands = {}
        self._load_commands()

    def add(self, name, command):
        """Registers command under specified name.
        :param name: command name
        :type name: str
        :param command: command class
        :type command: abstract.Command
        """

        self._commands[name] = command

    def _load_commands(self):
        """Load all external (from an entry points) commands."""

        for command in [Configure, Providers]:
            self.add(command.name, command)

    def get(self, name):
        """Gets command from command registry.
        Get registered command processor. Returns none if there is no
        such command registered. Raise ValueError if bad command value
        provided.
        :param name: command name from argv
        :type name: str
        """

        return self._commands.get(name, None)

    def __contains__(self, name):
        return name in self._commands

    def __getitem__(self, item):
        return self._commands[item]

    def __iter__(self):
        for key, value in self._commands.items():
            yield key, value
