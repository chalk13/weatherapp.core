"""Decorators for the weather application."""

import time


def slow_down_one_second(func):
    """Waits one second before calling function."""

    def wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)

    return wrapper


def slow_down(seconds=1):
    """Waits some time before calling function."""
    def one_second(func):
        """Waits one second before calling function."""

        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            return func(*args, **kwargs)

        return wrapper
    return one_second


@slow_down(seconds=3)
def hello(name):
    """Test function"""
    print(f'Hello {name}')


hello('Peter')
