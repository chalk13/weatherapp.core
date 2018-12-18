class ProviderManager:
    """Discovers registered providers and load them"""

    def __init__(self):
        self._providers = {}

    def add(self, name, provider):
        """Add new provider by name"""

        self._providers[name] = provider

    def get(self, name):
        """Get provider by name"""

        return self._providers.get([name], None)
