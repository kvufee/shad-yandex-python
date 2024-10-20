def find_value(nums: list[int] | range, value: int) -> bool:
    """
    Find value in sorted sequence
    :param nums: sequence of integers. Could be empty
    :param value: integer to find
    :return: True if value exists, False otherwise
    """
    l_idx = 0
    r_idx = len(nums) - 1

    if len(nums) == 0:
        return False

    while l_idx <= r_idx:
        cur = (l_idx + r_idx) // 2

        if nums[cur] < value:
            l_idx = cur + 1
        elif nums[cur] > value:
            r_idx = cur - 1
        else:
            return True

    return False
