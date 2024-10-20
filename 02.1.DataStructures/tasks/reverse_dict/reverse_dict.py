import typing as tp


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    dct_new: dict[str, list[str]] = {}
    for key, value in dct.items():
        if value not in dct_new:
            dct_new[value] = []
        dct_new[value].append(key)

    return dct_new
