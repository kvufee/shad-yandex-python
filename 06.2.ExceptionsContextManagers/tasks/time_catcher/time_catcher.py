import time
from typing import Optional, Type
from types import TracebackType


class TimeoutException(Exception):
    pass


class SoftTimeoutException(TimeoutException):
    pass


class HardTimeoutException(TimeoutException):
    pass


class TimeCatcher:
    def __init__(self, soft_timeout: Optional[float] = None, hard_timeout: Optional[float] = None):
        if (hard_timeout is not None and hard_timeout <= 0) or (soft_timeout is not None and soft_timeout <= 0):
            raise AssertionError("Timeout values should be above zero")
        if (soft_timeout is not None and hard_timeout is not None) and hard_timeout < soft_timeout:
            raise AssertionError("Soft timeout should be less than hard timeout")

        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self) -> 'TimeCatcher':
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        self.end_time = time.time()
        total_time = self.elapsed_time()

        if self.soft_timeout is not None and total_time > self.soft_timeout:
            raise SoftTimeoutException(f"{self.soft_timeout}")

        if self.hard_timeout is not None and total_time > self.hard_timeout:
            raise HardTimeoutException(f"{self.hard_timeout}")

    def elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def __float__(self) -> float:
        return self.elapsed_time()

    def __str__(self) -> str:
        return f"Time consumed: {self.elapsed_time()}"
