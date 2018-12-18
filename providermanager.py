class ProviderManager:
    """Discovers registered providers and load them"""

    def __init__(self):
        self._providers = {}
    