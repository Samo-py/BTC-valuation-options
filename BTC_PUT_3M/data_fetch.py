import asyncio
import websockets
import json
import datetime
import pandas as pd


def end_date(instrument_name):
    mesiace = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
        }
    
    date = instrument_name.split("-")[1]

    return int(str(20) + str(date[5:])), int(mesiace[date[2:5]]), int(date[:2])


async def fetch_data(ws, lock, instrument_name):
    msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/get_tradingview_chart_data",
            "params": {
                "instrument_name" : instrument_name,
                "start_timestamp" : int(datetime.datetime(2018, 1, 1).timestamp() * 1000),
                "end_timestamp" : int(datetime.datetime(*end_date(instrument_name)).timestamp() * 1000),
                "resolution" : "D"
            }
        }
    async with lock:
        try:
            await ws.send(json.dumps(msg))
            response = await ws.recv()
            response = json.loads(response)

        except websockets.ConnectionClosed:
            print(f"Connection closed while fetching {instrument_name}, will reconnect.")
            raise

        except Exception as e:
            print(f"Connection lost for {instrument_name}: {e}")
            return "error"

    if 'error' in response:
        print(response['error']['data']['reason'], instrument_name)
        return "error"
    
    elif response['result']['status'] == 'no_data':
        print('instrument data not found', instrument_name)
        return "error"

    else:
        dataframe = pd.DataFrame({
            "date": pd.to_datetime(response["result"]["ticks"], unit="ms").date.astype(str),
            "price_btc": response["result"]["close"]
        }).set_index("date")
        if pd.to_datetime(dataframe.index[-1]) - pd.to_datetime(dataframe.index[0]) >= pd.Timedelta(days=95):
            print('valid instrument found', instrument_name)
            return instrument_name, dataframe
        else:
            print('invalid instrument found', instrument_name)
            return "invalid instrument"

        
async def data_fetch(instrument_names : list, ws):
    tasks = []
    lock = asyncio.Lock()


    i = 0
    while i < len(instrument_names):
        async with asyncio.TaskGroup() as tg:
            for _ in range(min(5, len(instrument_names) - i)):
                task = tg.create_task(fetch_data(ws, lock, instrument_names[i]))
                tasks.append(task)
                i += 1

        if i < len(instrument_names):
            print(f"Sleeping 10s before burst, tasks : {i}")
            await asyncio.sleep(10)

    result_names = []
    result_dataframes = []

    for task in tasks:
        if len(task.result()) == 2:
            result_names.append(task.result()[0])
            result_dataframes.append(task.result()[1])
    
    try:
        pairs = list(zip(result_names, result_dataframes))
        pairs.sort(key=lambda x: int(x[0].split("-")[2]))
        result_names, result_dataframes = map(list, zip(*pairs))

    except:
        print("Empty month")
        raise


    return result_dataframes, result_names

# if __name__ == "__main__":
#     dataframes, names = asyncio.run(data_fetch(['BTC-29OCT21-20000-P']))
#     print(dataframes)