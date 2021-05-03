import json
import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin

from QAMarket.binance_order import fetch_binance_ohlcv
from QAMarket.okex_order import fetch_okex_ohlcv


def fetch_symbol_history_candle_data(ex, symbol, time_interval, max_len):
    # 获取当前时间
    since = int(time.time() * 1e3)

    # 循环获取历史数据
    all_kline_data = []
    while len(all_kline_data) < max_len:
        if ex == "okex":
            kline_data = fetch_okex_ohlcv(symbol, since, time_interval)
        elif ex == "binance":
            kline_data = fetch_binance_ohlcv(symbol, since, time_interval)
        else:
            print("请选择交易所")
            return

        if kline_data:
            since = int(kline_data[-1][0])
            all_kline_data += kline_data

    # 对数据进行整理
    df = pd.DataFrame(all_kline_data, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]

    # 删除重复的数据
    df.drop_duplicates(subset=['candle_begin_time_GMT8'], keep='last', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 为了保险起见，去掉最后一行最新的数据
    df = df[:-1]

    print(symbol, '获取历史数据行数：', len(df))
    return df

def fetch_candle_data(ex, symbol, since=None, time_interval='1m', limit=100):
    if ex == "okex":
        data = fetch_okex_ohlcv(symbol=symbol, timeframe=time_interval, limit=limit)
    elif ex == "binance":
        data = fetch_binance_ohlcv(symbol=symbol, timeframe=time_interval, limit=limit)
    else:
        print("请选择交易所")
        return

    # 整理数据
    df = pd.DataFrame(data, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high',
                       3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
    return df

# 获取需要的K线数据，并检测质量。
def get_candle_data(ex, symbol_config, time_interval, run_time, max_try_amount, candle_num, symbol):
    # 标记开始时间
    start_time = datetime.now()
    print('开始获取K线数据：', symbol, '开始时间：', start_time)

    # 获取数据合约的相关参数
    instrument_id = symbol_config[symbol]["instrument_id"]  # 合约id
    signal_price = None

    # 尝试获取数据
    for i in range(max_try_amount):
        df = fetch_candle_data(ex, instrument_id, time_interval, limit=candle_num)
        if df.empty:
            continue  # 再次获取

        else:  # 获取到了最新数据
            signal_price = df.iloc[-1]['close']  # 该品种的最新价格
            df = df[df['candle_begin_time_GMT8'] < pd.to_datetime(run_time)]  # 去除run_time周期的数据
            print('最新信号价格', signal_price, '结束获取K线数据', symbol, '结束时间：', datetime.now())
            return symbol, df, signal_price

    print('获取candle_data数据次数超过max_try_amount，数据返回空值')
    return symbol, pd.DataFrame(), signal_price

def single_threading_get_data(ex, symbol_info, symbol_config, time_interval, run_time, candle_num, max_try_amount=5):
    # 函数返回的变量
    symbol_candle_data = {}
    for symbol in symbol_config.keys():
        symbol_candle_data[symbol] = pd.DataFrame()

    # 逐个获取symbol对应的K线数据
    for symbol in symbol_config.keys():
        _, symbol_candle_data[symbol], symbol_info.at[symbol, '信号价格'] = get_candle_data(ex, symbol_config, time_interval, run_time, max_try_amount, candle_num, symbol)

    return symbol_candle_data