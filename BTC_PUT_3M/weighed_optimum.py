import asyncio
import pandas as pd
import numpy as np
import time
import random
import websockets

import subprocess
import atexit

from generate_options import generate_list_options
from generate_options import last_friday
from data_fetch import data_fetch
from price import live_price


def month_skip(date):
    month = int(date.split('-')[1])
    year = int(date.split('-')[0])

    if month + 1 == 13:
        month = 1
        year = year + 1
    else:
        month = month + 1

    if len(str(month)) == 1:
        return str(year) + "-" + "0" + str(month) + "-" + date.split("-")[2]
    else:
        return str(year) + "-" + str(month) + "-" + date.split("-")[2]


def end_date(instrument_name):
    mesiace = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
        }
    
    date = instrument_name.split("-")[1]

    return str(20) + str(date[5:]) + "-" + mesiace[date[2:5]] + "-" + date[:2]


class DataLoader:
    def __init__(self, left_bound, right_bound, step):
        self.step = step
        self.left_bound = left_bound
        self.right_bound = right_bound


    async def load(self):
        dataframes = []
        list_valid_names = []
        price_df = await live_price()
        list_option_names = generate_list_options(month_skip(self.left_bound), self.right_bound, price_df, self.step)

        async with websockets.connect("wss://www.deribit.com/ws/api/v2") as ws:
            print("Connection opened")
            poc = 0
            for names in list_option_names:
                data, valid_names = await data_fetch(names, ws)
                dataframes.append(data)
                list_valid_names.append(valid_names)

                poc += 1
                if poc < len(list_option_names):
                    await asyncio.sleep(10)

        for i in range(20):
            time.sleep(abs(random.gauss(0.1, 0.2)))
            subprocess.Popen(["afplay", "hollow_hit.mp3"])
        
        return dataframes, list_valid_names, price_df
    

class Pipeline:
    def __init__(self, price_df, dataframes, list_valid_names, first_date):
        self.price_df = price_df
        self.dataframes = dataframes
        self.list_valid_names = list_valid_names
        self.first_date = first_date

    def optimize(self):
        first_date = self.first_date
        optimal_ratios = []
        optimal_returns = []
        for i in range(len(self.dataframes)):
            ratios = np.zeros(len(self.dataframes[i]))
            returns = np.zeros(len(self.dataframes[i]))

            for j in range(len(self.dataframes[i])):
                ratios[j] = float(self.list_valid_names[i][j].split("-")[2]) / self.price_df["market_price"].loc[first_date]

                if float(self.list_valid_names[i][j].split("-")[2]) - self.price_df["market_price"].loc[self.dataframes[i][j].index[-1]] < 0:
                    returns[j] = 0
                else:
                    returns[j] = (float(self.list_valid_names[i][j].split("-")[2]) - self.price_df["market_price"].loc[self.dataframes[i][j].index[-1]]) / (self.dataframes[i][j]["price_btc"].loc[first_date] * self.price_df["market_price"].loc[first_date])
            if returns.sum() <= 0:
                optimal_ratios.append(0)
                optimal_returns.append(0)
            else:
                weighed_average = np.average(ratios, weights=returns)
                optimal_ratios.append(weighed_average)
                optimal_returns.append(returns[np.argmin(np.abs(ratios - weighed_average))])

            first_date = end_date(self.list_valid_names[i][0])

        optimal_ratios = np.array(optimal_ratios)
        optimal_returns = np.array(optimal_returns)
        self.optimum = np.average(optimal_ratios, weights=optimal_returns)

        return self

    def optimal_returns(self):
        first_date = self.first_date
        optimal_returns = []
        for i in range(len(self.dataframes)):
            ratios = np.zeros(len(self.dataframes[i]))
            for j in range(len(self.dataframes[i])):
                ratios[j] = float(self.list_valid_names[i][j].split("-")[2]) / self.price_df["market_price"].loc[first_date]
            index = np.argmin(np.abs(ratios - (self.optimum)))
            ### debugging
            print(first_date)
            print(self.list_valid_names[i][index])
            ### debugging
            if (float(self.list_valid_names[i][index].split("-")[2]) - self.price_df["market_price"].loc[self.dataframes[i][index].index[-1]]) / (self.dataframes[i][index]["price_btc"].loc[first_date] * self.price_df["market_price"].loc[first_date]) < 0:
                optimal_returns.append(0)
            else:
                optimal_returns.append((float(self.list_valid_names[i][index].split("-")[2]) - self.price_df["market_price"].loc[self.dataframes[i][j].index[-1]]) / (self.dataframes[i][index]["price_btc"].loc[first_date] * self.price_df["market_price"].loc[first_date]))

            first_date = end_date(self.list_valid_names[i][0])
            

        optimal_returns = np.array(optimal_returns)

        return optimal_returns, self.optimum, np.average(optimal_returns)
    
async def weighed_optimum():
    ### prvé to nestahuje lebo start
    ### treba ukontrolovat ci to funguje vzhladom na backtest zo zaciatku 1, 2, 3 mes a potom 3 mes


    ### generate options max strike je 1.5x viac ako pri 1 mes a spodna hranica je zmenena
    left_bound = '2021-09-01'
    right_bound = '2022-11-01'
    step = 2500

    dataframes, list_valid_names, price_df = await DataLoader(left_bound, right_bound, step).load()
    first_date = last_friday(int(left_bound.split("-")[0]), int(left_bound.split("-")[1]))

    if len(dataframes) > 0:
        optimal_returns, optimum, optimal_return = Pipeline(price_df, dataframes, list_valid_names, first_date).optimize().optimal_returns()
        print(optimal_returns)
        print(optimum, optimal_return)
    else:
        print("invalid bounds for backtest")


if __name__ == "__main__":
    proc = subprocess.Popen(["caffeinate", "-dimsu"])
    atexit.register(proc.terminate)
    
    asyncio.run(weighed_optimum())


