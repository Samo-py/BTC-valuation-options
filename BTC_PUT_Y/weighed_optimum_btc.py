import pandas as pd
import numpy as np
import asyncio
import os
import sys

import time
import random
import subprocess

from generate_options import generate_options
from data_fetch import data_fetch

sys.path.insert(0, os.getcwd())
from BTC_model.master_coupler import master_coupler


def model_signal(dataframe: pd.DataFrame, maximum: float, maximum_coef: float, model_coef: float):
    return dataframe[(dataframe['market'] >= maximum_coef * maximum) & (dataframe['market'] >= dataframe['model'] * model_coef)]


class Pipeline:
    def __init__(self, model_df: pd.DataFrame, dataframes: list, names: list, dates: list):
        self.model_df = model_df
        self.dataframes = dataframes
        self.names = names
        self.dates = dates
        self.optimum = self.optimize()


    def optimize(self):
        optimal_ratios = []
        optimal_returns = []

        for date in self.dates:
            ratios = np.zeros(len(self.dataframes))
            returns = np.zeros(len(self.dataframes))
            for i, name in enumerate(self.names):
                ratios[i] = float(name.split('-')[2]) / self.model_df['market'][date]
                returns[i] = self.dataframes[i]['price'].iloc[-1] / self.dataframes[i]['price'][date]
            weighed_average = np.average(ratios, weights=returns)
            optimal_ratios.append(weighed_average)
            optimal_returns.append(returns[np.argmin(np.abs(ratios - weighed_average))])
        optimal_ratios = np.array(optimal_ratios)
        optimal_returns = np.array(optimal_returns)
        optimum = np.average(optimal_ratios, weights=optimal_returns)
        
        return optimum


    def optimal_returns(self):
        optimal_returns = []

        for date in self.dates:
            ratios = np.zeros(len(self.dataframes))
            for i, name in enumerate(self.names):
                ratios[i] = float(name.split('-')[2]) / self.model_df['market'][date]
            index = np.argmin(np.abs(ratios - self.optimum))
            optimal_returns.append(self.dataframes[index]['price'].iloc[-1] / self.dataframes[index]['price'][date])
        
        optimal_returns = np.array(optimal_returns)
        return self.optimum, np.average(optimal_returns)


def weighed_optimum():
    left_bound = '2021-06-01'
    right_bound = '2023-06-01'
    maximum_coef = 0.8
    model_coef = 2


    dataframes, names = asyncio.run(data_fetch(generate_options(2022, 9, 60000, 2500)))
    model = master_coupler().astype({"date": str}).set_index("date")
    signal = model_signal(model.loc[left_bound:right_bound], max(model.loc[:left_bound]['market']), maximum_coef, model_coef).index
    dates = np.array(signal)[signal >= "2021-09-30"]
    

    pipeline = Pipeline(model, dataframes, names, dates)
    optimum, optimal_returns = pipeline.optimal_returns()
    return optimum, optimal_returns


if __name__ == "__main__":
    print(*weighed_optimum())
    for i in range(20):
        time.sleep(abs(random.gauss(0.05, 0.15)))
        subprocess.Popen(["afplay", "hollow_hit.mp3"])