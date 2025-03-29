import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import time
import os
from dotenv import load_dotenv

api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

load_dotenv() 
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
ts = TimeSeries(key=api_key, output_format='pandas')

def fetch_intraday_data(symbol, interval='1min', outputsize='full'):
    try:
        data, meta_data = ts.get_intraday(symbol=symbol, interval=interval, outputsize=outputsize)
        data['Symbol'] = symbol
        return data
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")
        return None

def moving_average_crossover_strategy(symbol, data):
    print("Columns in the data:", data.columns)

    data['SMA_50'] = data['4. close'].rolling(window=50).mean()  # 50-period simple moving average
    data['SMA_200'] = data['4. close'].rolling(window=200).mean()  # 200-period simple moving average
    
    # buy/sell signals based on moving averages
    data['Signal'] = 0
    data.iloc[50:, data.columns.get_loc('Signal')] = np.where(data['SMA_50'][50:] > data['SMA_200'][50:], 1, 0) 
    data['Position'] = data['Signal'].diff()  
    
    print(f"\nTrade signals for {symbol}:")
    print(data[['4. close', 'SMA_50', 'SMA_200', 'Signal', 'Position']].tail(10))

    plt.figure(figsize=(12,6))
    plt.plot(data.index, data['4. close'], label=f'{symbol} Price')
    plt.plot(data.index, data['SMA_50'], label='50-period SMA', alpha=0.7)
    plt.plot(data.index, data['SMA_200'], label='200-period SMA', alpha=0.7)
    plt.scatter(data.index[data['Position'] == 1], data['SMA_50'][data['Position'] == 1], marker='^', color='g', label='Buy Signal', alpha=1)
    plt.scatter(data.index[data['Position'] == -1], data['SMA_50'][data['Position'] == -1], marker='v', color='r', label='Sell Signal', alpha=1)
    plt.title(f'{symbol} Moving Average Crossover Strategy')
    plt.legend()
    plt.show()

def run_strategy(symbols):
    all_data = {}
    for symbol in symbols:
        print(f"\nDownloading data for {symbol}...")
        data = fetch_intraday_data(symbol)
        if data is not None:
            all_data[symbol] = data
            moving_average_crossover_strategy(symbol, data)
        time.sleep(12)  # prevent hitting API limits

symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

run_strategy(symbols)

start_time = time.time()

for i in range(1000000):
    pass

elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time} seconds")
