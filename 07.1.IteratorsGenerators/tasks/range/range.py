from collections.abc import Iterable, Iterator, Sized


class RangeIterator(Iterator[int]):
    """The iterator class for Range"""
    def __init__(self, range_: 'Range') -> None:
        self._range = range_
        self._current = range_.start

    def __iter__(self) -> 'RangeIterator':
        return self

    def __next__(self) -> int:
        if (self._range.step > 0 and self._current >= self._range.stop) or (self._range.step < 0 and self._current <= self._range.stop):
            raise StopIteration
        current = self._current
        self._current += self._range.step
        return current


class Range(Sized, Iterable[int]):
    """The range-like type, which represents an immutable sequence of numbers"""

    def __init__(self, *args: int) -> None:
        if len(args) == 1:
            self.start = 0
            self.stop = args[0]
            self.step = 1
        elif len(args) == 2:
            self.start = args[0]
            self.stop = args[1]
            self.step = 1
        elif len(args) == 3:
            self.start = args[0]
            self.stop = args[1]
            self.step = args[2]
            if self.step == 0:
                raise ValueError("Step must not be zero.")
        else:
            raise TypeError("Range expected at most 3 arguments, got {}".format(len(args)))

        if self.step < 0 and self.start < self.stop:
            raise ValueError("Step is negative, but start is less than stop.")
        if self.step > 0 and self.start > self.stop:
            raise ValueError("Step is positive, but start is greater than stop.")

    def __iter__(self) -> 'RangeIterator':
        return RangeIterator(self)

    def __repr__(self) -> str:
        return f"Range({self.start}, {self.stop}, {self.step})"

    def __str__(self) -> str:
        return f"range({self.start}, {self.stop}, {self.step})"

    def __contains__(self, key: int) -> bool:
        if self.step > 0:
            return self.start <= key < self.stop and (key - self.start) % self.step == 0
        else:
            return self.stop < key <= self.start and (self.start - key) % (-self.step) == 0

    def __getitem__(self, key: int) -> int:
        if key < 0:
            raise IndexError("Negative indexing is not supported.")
        if self.step > 0:
            value = self.start + key * self.step
            if value >= self.stop:
                raise IndexError("Index out of range.")
            return value
        else:
            value = self.start + key * self.step
            if value <= self.stop:
                raise IndexError("Index out of range.")
            return value

    def __len__(self) -> int:
        if self.step > 0:
            if self.start >= self.stop:
                return 0
            return (self.stop - self.start + self.step - 1) // self.step
        else:
            if self.start <= self.stop:
                return 0
            return (self.start - self.stop - self.step - 1) // -self.step
