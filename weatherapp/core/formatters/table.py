"""Table formatter class for the weather application."""

from typing import Union

import prettytable

from weatherapp.core.abstract import Formatter


class TableFormatter(Formatter):
    """Table formatter for application output."""

    @staticmethod
    def emit(column_names: list, data: Union[list, tuple]):
        """Format and print data from the iterable source."""

        pretty = prettytable.PrettyTable()

        for column, values in zip(column_names, (data.keys(), data.values())):
            if any(values):
                pretty.add_column(column, list(values))

        pretty.align = 'l'
        pretty.padding_width = 1
        return pretty.get_string()
