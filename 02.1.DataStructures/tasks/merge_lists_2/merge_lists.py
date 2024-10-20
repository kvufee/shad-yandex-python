import heapq
import typing as tp


def merge(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    """
    :param seq: sequence of sorted sequences
    :return: merged sorted list
    """
    min_heap: list[tuple[int, int, int]] = []
    result = []

    for i, lst in enumerate(seq):
        if lst:
            heapq.heappush(min_heap, (lst[0], i, 0))

    while min_heap:
        value, list_index, element_index = heapq.heappop(min_heap)
        result.append(value)

        if element_index + 1 < len(seq[list_index]):
            next_value = seq[list_index][element_index + 1]
            heapq.heappush(min_heap, (next_value, list_index, element_index + 1))

    return result
