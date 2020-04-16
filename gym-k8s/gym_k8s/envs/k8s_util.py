import re
import time
import datetime

# parse datetime to utc timestamp
def parse_clock(clock):
    s = re.split(r'[-T:+]', clock)
    year_s = s[0]
    month_s = s[1]
    day_s = s[2]
    hour_s = s[3]
    minute_s = s[4]
    second_s = s[5]
    hour_shift_s = s[6]
    minute_shift_s = s[7]

    local_dt = datetime.datetime(int(year_s), int(month_s), int(day_s), int(hour_s), int(minute_s), int(second_s))
    utc_dt = local_dt - datetime.timedelta(hours=int(hour_shift_s), minutes=int(minute_shift_s))
    utc_ts = time.mktime(utc_dt.timetuple())

    return utc_ts

if __name__ == '__main__':
    clock = "2019-01-01T03:19:40+09:00"

    parse_clock(clock)