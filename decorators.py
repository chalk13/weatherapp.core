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
    """Hello test function."""
    print(f'Hello {name}')


def timer(func):
    """Finds function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # performance counter
        result = func(*args, **kwargs)
        run_time = time.perf_counter() - start_time
        print(f'Function ({func.__name__!r}) execution time '
              f'is {run_time:.4f} seconds.')
        return result

    return wrapper


@timer
def sleep(sec):
    """Sleep test function."""
    time.sleep(sec)



