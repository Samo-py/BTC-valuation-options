import datetime
import calendar


def last_friday(year, month):

    last_day = calendar.monthrange(year, month)[1]
    d = datetime.date(year, month, last_day)

    while d.weekday() != 4:
        d = d.replace(day=d.day - 1)
    return d

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

def generate_strikes(end: int, step: int):
    count = end // step
    return [(i + 1) * step for i in range(count)]

def generate_options(expiry_year, expiry_month, max_strike, step):
    strikes = generate_strikes(max_strike, step)
    instrument_names = generate_instrument_names(str(last_friday(expiry_year, expiry_month)).split('-'), strikes)
    return instrument_names




