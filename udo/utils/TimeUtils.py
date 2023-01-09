import time


def date_to_timestamp(date):
    return time.mktime(time.strptime(date, "%Y-%m-%d"))


def date_time_to_timestamp(date_time):
    return time.mktime(time.strptime(date_time, "%Y-%m-%d %H:%M:%S"))


def timestamp_to_date(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))


def timestamp_to_date_time(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def get_struct_time_from_date(date):
    return time.localtime(date_to_timestamp(date))


def get_struct_time_from_date_time(date_time):
    return time.localtime(date_time_to_timestamp(date_time))


def get_struct_time_from_timestamp(timestamp):
    return time.localtime(timestamp)


if __name__ == '__main__':

    dt = "2016-05-06"
    dt2 = "2016-05-05 20:28:54"
    now = int(time.time())

    print(date_to_timestamp(dt))
    print(get_struct_time_from_date(dt))
    print(date_time_to_timestamp(dt2))
    print(get_struct_time_from_date_time(dt2))

    print(timestamp_to_date(now))
    print(timestamp_to_date_time(now))
    print(get_struct_time_from_timestamp(now))




