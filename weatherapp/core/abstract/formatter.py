import abc
from typing import Union


class Formatter(abc.ABC):
    """Base abstract class for formatters."""

    @abc.abstractmethod
    def emit(self, column_names: list, data: Union[list, tuple]):
        """Format and print data from the iterable source."""
