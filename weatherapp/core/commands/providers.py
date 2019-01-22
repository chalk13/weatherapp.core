"""Providers command class for the weather application."""

from weatherapp.core.abstract.command import Command


class Providers(Command):
    """Prints all available providers."""

    name = 'providers'

    def run(self, argv):
        """Prints the number and the provider name."""
        print(f"Available providers (provider id):")
        for number, provider in enumerate(self.app.providermanager._providers.values(), 1):
            print(f'{number}. {provider.title} ({provider.name})')
