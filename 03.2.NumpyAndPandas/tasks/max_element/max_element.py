import numpy as np
import numpy.typing as npt


def max_element(array: npt.NDArray[np.int_]) -> int | None:
    """
    Return max element before zero for input array.
    If appropriate elements are absent, then return None
    :param array: array,
    :return: max element value or None
    """
    zeros = np.where(array == 0)[0]

    good = zeros + 1
    good = good[good < len(array)]
    if good.size == 0:
        return None

    return array[good].max()
