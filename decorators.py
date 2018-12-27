"""Decorators for the weather application."""

import time


def slow_down_one_second(func):
    """Waits one second before calling function."""

    def wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)

    return wrapper


@slow_down_one_second
def hello(name):
    print(f'Hello {name}')


hello('Peter')
