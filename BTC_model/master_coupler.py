import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import asyncio

from BTC_model.pipelines.live_hash import live_hash
from BTC_model.pipelines.live_price import live_price

from BTC_model.pipelines.environment_pipeline import environment_pipeline
from BTC_model.pipelines.emission_pipeline import emission_pipeline
from BTC_model.pipelines.machines_pipeline import machines_pipeline
from BTC_model.pipelines.electricity_pipeline import electricity_pipeline



class DataLoader:
    def __init__(self, rate_df: pd.DataFrame, antminers_df: pd.DataFrame, environment_df: pd.DataFrame, electricity_df: pd.DataFrame ,emission_df: pd.DataFrame, halving_dates: np.ndarray):
        self.df = pd.merge(pd.merge(pd.merge(pd.merge(rate_df, antminers_df, how='inner', on='date'), environment_df, how='inner', on='date'), emission_df, how='inner', on='date'), electricity_df, on='date',how='inner')
        self.halving_dates = halving_dates
        self.result_est = np.zeros(len(self.df['date']))
        self.timeseries = self.df['date']

    def run(self):
        self.result_est = ((((self.df['hash_rate'] / self.df['ant_hash_rate']) * self.df['ant_power']) * 24 * self.df['electricity']) / (self.df['emission'] * 144) * 2.5) * (self.df['env_efficiency'] / self.df['ant_efficiency'])

        return self
    
class Pipeline:
    def __init__(self, dates : np.ndarray, market_values : np.ndarray, model_values : np.ndarray):
        self.dates = dates
        self.model_values = model_values
        self.market_values = market_values

    def coupler(self, x, a, b, min, max):
        range_val = max - min
        norm = (x - a) / (b - a)
        t = np.clip(norm, 0, 1)
        s = 3*t**2 - 2*t**3

        return min + s*range_val

    def run(self):
        self.timeseries = pd.date_range(min(self.dates), max(self.dates), freq='D')
        self.market = np.zeros(len(self.timeseries))
        self.model = np.zeros(len(self.timeseries))

        for i in range(len(self.dates) - 1):
            mask = (self.timeseries >= self.dates[i]) & (self.timeseries <= self.dates[i + 1])
            self.market[mask] = self.coupler(self.timeseries[mask], self.dates[i], self.dates[i+1], self.market_values[i], self.market_values[i+1])
            self.model[mask] = self.coupler(self.timeseries[mask], self.dates[i], self.dates[i+1], self.model_values[i], self.model_values[i+1])
        

        df = pd.DataFrame({'date' : self.timeseries, 'model' : self.model, 'market' : self.market})
        self.df = df

        return self

def master_coupler():
    coef = 2

    price_df = asyncio.run(live_price())
    hash_df = asyncio.run(live_hash())
    price_df["date"] = pd.to_datetime(price_df["date"])
    hash_df["date"] = pd.to_datetime(hash_df["date"])
    df = pd.merge(hash_df, price_df, on="date", how="inner")
    dataloader = DataLoader(df, machines_pipeline(), environment_pipeline(), electricity_pipeline(), *emission_pipeline()).run()
    pipeline = Pipeline(dataloader.df['date'], dataloader.df['market_price'], dataloader.result_est).run()
    
    return pipeline.df
    

