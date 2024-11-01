import numpy as np
import numpy.typing as npt


def add_zeros(x: npt.NDArray[np.int_]) -> npt.NDArray[np.int_]:
    """
    Add zeros between values of given array
    :param x: array,
    :return: array with zeros inserted
    """
    if x.size == 0:
        return x

    res = np.zeros(2 * len(x) - 1, dtype=x.dtype)
    res[::2] = x

    return res
