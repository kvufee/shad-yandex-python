from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ_NAME = "Europe/Moscow"


def now() -> datetime:
    """Return now in default timezone"""
    return datetime.now(ZoneInfo(DEFAULT_TZ_NAME))


def strftime(dt: datetime, fmt: str) -> str:
    """Return dt converted to string according to format in default timezone"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME)).strftime(fmt)


def strptime(dt_str: str, fmt: str) -> datetime:
    """Return dt parsed from string according to format in default timezone"""
    dt = datetime.strptime(dt_str, fmt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))


def diff(first_dt: datetime, second_dt: datetime) -> int:
    """Return seconds between two datetimes rounded down to closest int"""
    if first_dt.tzinfo is None:
        first_dt = first_dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    if second_dt.tzinfo is None:
        second_dt = second_dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return int((second_dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME)) -
                first_dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))).total_seconds())


def timestamp(dt: datetime) -> int:
    """Return timestamp for given datetime rounded down to closest int"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return int(dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME)).timestamp())


def from_timestamp(ts: float) -> datetime:
    """Return datetime from given timestamp"""
    dt = datetime.fromtimestamp(ts, tz=ZoneInfo(DEFAULT_TZ_NAME))
    return dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
