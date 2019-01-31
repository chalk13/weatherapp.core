"""Manager to view registered providers and download them."""

from weatherapp.core.providers import AccuWeatherProvider, Rp5WeatherProvider
from weatherapp.core.providers import SinoptikWeatherProvider
from weatherapp.core.abstract import Manager


class ProviderManager(Manager):
    """Discovers registered providers and load them."""

    def __init__(self):
        self._providers = {}
        self._load_providers()

    def _load_providers(self):
        """Load all existing providers."""

        for provider in [AccuWeatherProvider,
                         Rp5WeatherProvider,
                         SinoptikWeatherProvider]:
            self.add(provider.name, provider)

    def add(self, name, provider):
        """Add new provider by name."""

        self._providers[name] = provider

    def get(self, name):
        """Get provider by name."""

        return self._providers.get(name, None)

    def __len__(self):
        return len(self._providers)

    def __contains__(self, name):
        return name in self._providers

    def __getitem__(self, item):
        return self._providers[item]

    def __iter__(self):
        for key, value in self._providers.items():
            yield key, value
