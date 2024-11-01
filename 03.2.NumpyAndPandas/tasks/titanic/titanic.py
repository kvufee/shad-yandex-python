import typing as tp

import pandas as pd


def male_age(df: pd.DataFrame) -> float:
    """
    Return mean age of survived men, embarked in Southampton with fare > 30
    :param df: dataframe
    :return: mean age
    """
    male_df = df[(df['Sex'] == 'male') & (df['Fare'] > 30) & (df['Embarked'] == 'S') & (df['Survived'] == 1)]
    return male_df['Age'].mean()


def nan_columns(df: pd.DataFrame) -> tp.Iterable[str]:
    """
    Return list of columns containing nans
    :param df: dataframe
    :return: series of columns
    """
    return df.columns[df.isna().any()].tolist()


def class_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return Pclass distrubution
    :param df: dataframe
    :return: series with ratios
    """
    return df['Pclass'].value_counts(normalize=True)


def families_count(df: pd.DataFrame, k: int) -> int:
    """
    Compute number of families with more than k members
    :param df: dataframe,
    :param k: number of members,
    :return: number of families
    """
    df['Surname'] = df['Name'].str.split(',').str[0]
    family_sizes = df.groupby('Surname').size()
    large_families = family_sizes[family_sizes > k].count()

    return large_families


def mean_price(df: pd.DataFrame, tickets: tp.Iterable[str]) -> float:
    """
    Return mean price for specific tickets list
    :param df: dataframe,
    :param tickets: list of tickets,
    :return: mean fare for this tickets
    """
    return df[df['Ticket'].isin(tickets)]['Fare'].mean()


def max_size_group(df: pd.DataFrame, columns: list[str]) -> tp.Iterable[tp.Any]:
    """
    For given set of columns compute most common combination of values of these columns
    :param df: dataframe,
    :param columns: columns for grouping,
    :return: list of most common combination
    """
    return df.groupby(columns).size().idxmax()


def isLucky(ticket: str) -> bool:
    if not ticket.isdigit() or len(ticket) % 2 != 0:
        return False

    first_half_sum = sum(int(digit) for digit in ticket[:len(ticket) // 2])
    second_half_sum = sum(int(digit) for digit in ticket[len(ticket) // 2:])

    return first_half_sum == second_half_sum


def dead_lucky(df: pd.DataFrame) -> float:
    """
    Compute dead ratio of passengers with lucky tickets.
    A ticket is considered lucky when it contains an even number of digits in it
    and the sum of the first half of digits equals the sum of the second part of digits
    ex:
    lucky: 123222, 2671, 935755
    not lucky: 123456, 62869, 568290
    :param df: dataframe,
    :return: ratio of dead lucky passengers
    """
    df['isLucky'] = df['Ticket'].apply(isLucky)

    lucky_to_dead_ratio = df[df['isLucky'] & (df['Survived'] == 0)].shape[0] / df[df['isLucky']].shape[0]

    return lucky_to_dead_ratio
