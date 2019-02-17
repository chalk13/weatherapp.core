"""Table formatter class for the weather application."""

from typing import Union

import prettytable

from weatherapp.core.abstract import Formatter


class TableFormatter(Formatter):
    """Table formatter for application output."""

    def emit(self, column_names: list, data: Union[list, tuple]):
        """Format and print data from the iterable source."""

        pt = prettytable.PrettyTable()

        for column, values in zip(column_names, (data.keys(), data.values())):
            if any(values):
                pt.add_column(column, list(values))

        pt.align = 'l'
        pt.padding_width = 1
        return pt.get_string()
