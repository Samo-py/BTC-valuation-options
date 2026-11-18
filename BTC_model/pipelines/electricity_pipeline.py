import pandas as pd
import numpy as np

class Dataloader:

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dates = None
        self.values = None
        self.df = None
    
    def load_emission(self):
        df = pd.read_csv(self.filepath)
        self.dates = pd.to_datetime(df['date']).to_numpy()
        self.values = df['electricity'].to_numpy()
        return self
    
    def load_fees(self):
        self.df = pd.read_csv(self.filepath)
        self.df['date'] = pd.to_datetime(self.df['date'])
        return self
    
class Pipeline:

    def __init__(self, dates: np.ndarray, values: np.ndarray):
        self.dates = dates
        self.values = values
        self.timeseries = None
        self.electricity = None

    def coupler(self, x, a, b, min, max):
        range_val = max - min
        norm = (x - a) / (b - a)
        t = np.clip(norm, 0, 1)
        s = 3*t**2 - 2*t**3
        return min + s*range_val 

    def run(self, end_date):
        self.timeseries = pd.date_range(min(self.dates), end_date, freq='D')
        self.electricity = np.zeros(len(self.timeseries))

        
        for i in range(len(self.dates) - 1):
            mask = (self.timeseries >= self.dates[i]) & (self.timeseries <= self.dates[i+1])
            self.electricity[mask] = self.coupler(self.timeseries[mask], self.dates[i], self.dates[i+1], self.values[i], self.values[i+1])
        mask = (self.timeseries >= self.dates[-1]) & (self.timeseries <= end_date)
        self.electricity[mask] = self.values[-1]

        return self
    
def electricity_pipeline():
    emission_path = 'BTC_model/data/electricity.csv'
    
    electricity_loader = Dataloader(emission_path).load_emission()
    pipeline = Pipeline(electricity_loader.dates, electricity_loader.values).run(electricity_loader.dates[-1])


    
    df =  pd.DataFrame({'date': pipeline.timeseries, 'electricity': pipeline.electricity})

    return df
