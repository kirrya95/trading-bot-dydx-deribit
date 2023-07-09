from datetime import datetime, timedelta
import pytz


# example: datetime.strptime("2023-07-01 00:00:00", "%Y-%m-%d %H:%M:%S")
def to_utc_timestamp(string_datetime):
    dt = datetime.strptime(string_datetime, "%Y-%m-%d %H:%M:%S")
    dt = pytz.UTC.localize(dt)

    return dt.timestamp()


def timedelta_to_str(seconds_difference):
    return timedelta(seconds=seconds_difference)


if __name__ == '__main__':
    print(to_utc_timestamp("2023-07-01 00:00:00"))
