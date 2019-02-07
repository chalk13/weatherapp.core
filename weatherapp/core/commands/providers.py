"""Providers command class for the weather application."""

from weatherapp.core.abstract.command import Command


class Providers(Command):
    """Prints all available providers."""

    name = 'providers'

    def run(self, argv):
        """Prints provider name and id."""
        for provider in self.app.providermanager._providers.values():
            self.stdout.write(f'{provider.title} ({provider.name})\n')
