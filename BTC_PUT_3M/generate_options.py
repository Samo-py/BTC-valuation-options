import datetime
import calendar
import pandas as pd

def last_friday(year, month):

    last_day = calendar.monthrange(year, month)[1]
    d = datetime.date(year, month, last_day)

    while d.weekday() != 4:
        d = d.replace(day=d.day - 1)
    return str(d)

def generate_instrument_names(date: str, strikes: list):
    mesiace = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
        5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
        9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
            }

    year = date[0][2:4]
    month = mesiace[int(date[1]) // 1]
    day = date[2]
    date = str(day) + str(month) + str(year)
    instrument_names = ['BTC-' + date + '-' + str(i) + '-P' for i in strikes]

    return instrument_names

def generate_strikes(start: int, end: int, step: int):
    count = (end - start) // step
    return [(i) * step for i in range(start // step, (start // step) + count + 1)]

def generate_options(expiry_year, expiry_month, min_strike, max_strike, step):
    strikes = generate_strikes(min_strike, max_strike, step)
    instrument_names = generate_instrument_names(last_friday(expiry_year, expiry_month).split('-'), strikes)
    return instrument_names


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


def generate_list_options(left_bound: str, right_bound: str, price_df: pd.DataFrame, step):
    data = month_year(left_bound, right_bound)
    result = []
    for key, values in data.items():
        for value in values:
            offset = value - 1
            year = key
            if offset == 0:
                offset = 12
                year = key - 1
            result.append(generate_options(key, value, ((int(price_df["market_price"].loc[last_friday(year, offset)] * 0.94 // 2500)) * 2500), ((int(price_df["market_price"].loc[last_friday(year, offset)] * 1.5 // 2500) + 1) * 2500), step))
    return result
