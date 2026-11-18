import asyncio
import aiohttp
import pandas as pd

async def live_price():
    url = "https://api.blockchain.info/charts/market-price?timespan=all&format=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            dataframe = pd.DataFrame(data["values"]).rename(columns={"x": "date", "y": "market_price"})
            dataframe["date"] = (pd.to_datetime(dataframe['date'], unit="s") - pd.Timedelta(days=1))
            dataframe = dataframe.astype({"date": str}).set_index("date")
            full_idx = pd.date_range(start=dataframe.index[0], end=dataframe.index[-1], freq="D").astype(str)
            dataframe = dataframe.reindex(full_idx)
            return dataframe.interpolate(method="linear")

if __name__ == "__main__":
    dataframe = asyncio.run(live_price())
    print(type(dataframe.index[-1]))