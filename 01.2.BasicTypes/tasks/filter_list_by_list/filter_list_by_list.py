def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    ans: list[int] = []
    i = 0
    j = 0

    if isinstance(lst_a, range):
        lst_a = list(lst_a)
    if isinstance(lst_b, range):
        lst_b = list(lst_b)

    if len(lst_b) == 0:
        return lst_a
    if len(lst_a) == 0:
        return []
    if len(lst_a) != len(lst_b):
        return []

    while i < len(lst_a) and j < len(lst_b):
        if lst_a[i] < lst_b[j]:
            ans.append(lst_a[i])
            i += 1
        elif lst_a[i] > lst_b[j]:
            j += 1
        else:
            i += 1
            j += 1

    while i < len(lst_a):
        ans.append(lst_a[i])
        i += 1

    return ans
