class ProviderManager:
    """Discovers registered providers and load them"""

    def __init__(self):
        self._providers = {}

    def get(self, name):
        """Get provider by name"""

        return self._providers.get([name], None)
    