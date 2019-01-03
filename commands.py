"""Weather application commands."""

from abstract import Command


class Configure(Command):
    """Customizes the location for the weather provider."""

    name = 'config'

    def get_argument_parser(self):
        """Initialize argument parser for command."""

        parser = super().get_argument_parser()
        parser.add_argument('provider', help='Provider name')
        return parser

    def run(self, argv):
        """Run command."""

        parsed_args = self.get_argument_parser().parse_args(argv)
        if parsed_args.provider:
            provider_name = parsed_args.provider
            if provider_name in self.app.providermanager:
                provider_factory = self.app.providermanager.get(provider_name)
                provider_factory(self.app).configuration(provider_name)


class Providers(Command):
    """Prints all available providers."""

    name = 'providers'

    def run(self, argv):
        """Prints the number and the provider name."""
        print(f"Available providers (provider id):")
        for number, provider in enumerate(self.app.providermanager._providers.values(), 1):
            print(f'{number}. {provider.title} ({provider.name})')
