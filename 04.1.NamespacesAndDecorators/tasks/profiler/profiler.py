from functools import wraps
from datetime import datetime


def profiler(func):  # type: ignore
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: `calls`, `last_time_taken`
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """
    calls = 0
    end_time = 0

    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        nonlocal calls
        nonlocal end_time

        calls += 1
        call = calls
        start_time = datetime.now()

        result = func(*args, **kwargs)
        end_time = (datetime.now() - start_time).total_seconds()

        wrapper.calls = calls - call + 1
        wrapper.last_time_taken = end_time

        return result

    wrapper.calls = 0
    wrapper.last_time_taken = 0.0

    return wrapper
