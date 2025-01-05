# Standard Library
from datetime import datetime, timedelta

# Third Party Stuff
import django.utils.timezone as django_dt


def now(with_tz: bool = False) -> datetime:
    if with_tz:
        return django_dt.now()
    else:
        return datetime.now()


def today(with_tz: bool = False):
    if with_tz:
        return django_dt.now().today()
    else:
        return datetime.today()


def time_after(secs: int, with_tz: bool = False) -> datetime:
    time = now(with_tz=with_tz)
    return time + timedelta(seconds=secs)


def get_local_curr_hour():
    return django_dt.now().hour


def get_secs_left_in_day():
    n = django_dt.now()
    seconds_left = ((24 - n.hour - 1) * 60 * 60) + ((60 - n.minute - 1) * 60) + (60 - n.second)
    return seconds_left


# def get_secs_left_in_day_in_ist():
#     from datetime import datetime

#     import pytz

#     local_tz = pytz.timezone("Asia/Calcutta")
#     n = datetime.now(tz=local_tz)
#     seconds_left = ((24 - n.hour - 1) * 60 * 60) + ((60 - n.minute - 1) * 60) + (60 - n.second)
#     return seconds_left


def get_next_day_start_timestamp_micro_sec():
    return (django_dt.now().timestamp() + get_secs_left_in_day()) * 1000000


# def get_specific_datetime(year, month, day):
#     import pytz

#     local_tz = pytz.timezone("Asia/Calcutta")
#     custom_date = django_dt.datetime(year, month, day, tzinfo=local_tz)
#     return custom_date


def get_date_without_time(with_tz: bool, before_days: int = 0) -> datetime:
    date_time = now(with_tz=with_tz)
    date_time = date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    return date_time - timedelta(days=before_days)


def get_seconds_passed_in_a_day():
    n = django_dt.now()
    seconds_passed = (n - n.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_passed
