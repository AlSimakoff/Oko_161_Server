from datetime import datetime, timedelta
from databaseMySQL import select_by_time_range, select_last_n_days

def get_today_entry_count(table_name):
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    return len(select_by_time_range(table_name, start, end))

def get_average_time(table_name):
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    rows = select_by_time_range(table_name, start, end)

    times = [row[1] for row in rows if isinstance(row[1], datetime)]
    times.sort()
    if len(times) < 2:
        return 0
    total_diff = sum((t2 - t1).total_seconds() for t1, t2 in zip(times, times[1:]))
    return round(total_diff / 60 / (len(times) - 1), 2)

def get_recognition_errors(table_name):
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    rows = select_by_time_range(table_name, start, end)
    return sum(1 for row in rows if not row[3] or row[3].strip() == '')

def get_monthly_count(table_name):
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return len(select_by_time_range(table_name, start, now))

def get_hourly_data(table_name):
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    rows = select_by_time_range(table_name, start, end)

    hours = [0] * 24
    for row in rows:
        if isinstance(row[1], datetime):
            hours[row[1].hour] += 1
    return hours

def get_weekly_data(table_name):
    rows = select_last_n_days(table_name, 7)
    days = [0] * 7
    for row in rows:
        if isinstance(row[1], datetime):
            days[row[1].weekday()] += 1
    return days