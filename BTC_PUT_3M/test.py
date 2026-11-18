import datetime

def month_year(left_bound, right_bound):
    start_date = datetime.datetime.strptime(left_bound, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(right_bound, "%Y-%m-%d").date()
    

    year, month = start_date.year, start_date.month

    if month % 3 != 0:
        month = (month // 3 + 1) * 3
    result = {}

    while (year < end_date.year) or (year == end_date.year and month <= end_date.month):
        result.setdefault(year, []).append(month)
        month += 3
        if month > 12:
            month = 3
            year += 1

    return result

left = "2021-01-01"
right = "2023-01-01"

print(month_year(left, right))