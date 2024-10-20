import typing as tp

from collections import UserList


class ListTwist(UserList[tp.Any]):
    """
    List-like class with additional attributes:
        * reversed, R - return reversed list
        * first, F - insert or retrieve first element;
                     Undefined for empty list
        * last, L -  insert or retrieve last element;
                     Undefined for empty list
        * size, S -  set or retrieve size of list;
                     If size less than list length - truncate to size;
                     If size greater than list length - pad with Nones
    """
    def __getattr__(self, item: str) -> tp.Any:
        if item == 'reversed' or item == 'R':
            return list(reversed(self.data))

        if item == 'first' or item == 'F':
            if not self.data:
                raise IndexError()
            return self.data[0]

        if item == 'last' or item == 'L':
            if not self.data:
                raise IndexError()
            return self.data[-1]

        if item == 'size' or item == 'S':
            return len(self.data)

        raise AttributeError()

    def __setattr__(self, key: str, value: tp.Any) -> None:
        if key == 'first' or key == 'F':
            if not self.data:
                raise IndexError()
            self.data[0] = value
            return

        if key == 'last' or key == 'L':
            if not self.data:
                raise IndexError()
            self.data[-1] = value
            return

        if key == 'size' or key == 'S':
            cur_size = len(self.data)
            if value < cur_size:
                self.data = self.data[:value]
            if value > cur_size:
                self.data.extend([None] * (value - cur_size))
            return

        super().__setattr__(key, value)
