"""Configuration command class for the weather application."""

from weatherapp.core.abstract.command import Command


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
