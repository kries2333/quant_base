import json
import time
import pandas as pd
import requests
import datetime
from urllib.parse import urljoin

OKEx_base_url = 'https://www.okex.com'

def fetch_ohlcv(symbol, since=None, timeframe='1m', limit=100):
    # 请求数据
    url = urljoin(
        OKEx_base_url,
        '/api/v5/market/candles'
    )

    if (since == None):
        params={
                    "instId": symbol,
                    "bar": timeframe,
                    "limit": limit
                }
    else:
        params={
                    "instId": symbol,
                    "after": since,  # Z结尾的ISO时间 String
                    "bar": timeframe,
                    "limit": limit
                }

    retries = 1
    while (retries != 0):
        try:
            req = requests.get(
                url,
                params=params
            )
            # 防止频率过快
            time.sleep(0.5)
            retries = 0
        except (ConnectionError):
            retries = 1

        if (retries == 0):
            # 成功获取才处理数据，否则继续尝试连接
            msg_dict = json.loads(req.content)
            return msg_dict['data']

    return None


def okex_fetch_candle_data(symbol, since=None, time_interval='1m', limit=100):
    data = fetch_ohlcv(symbol=symbol, timeframe=time_interval, limit=limit)
    # 整理数据
    df = pd.DataFrame(data, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high',
                       3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + datetime.timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
    return df


# 获取历史数据
def fetch_okex_symbol_history_candle_data(symbol, time_interval, max_len):
    # 获取当前时间
    now_milliseconds = int(time.time() * 1e3)

    # 每根K线的间隔时间
    time_interval_int = int(time_interval[:-1])  # 若15m，则time_interval_int = 15；若2h，则time_interval_int = 2
    if time_interval.endswith('m'):
        time_segment = time_interval_int * 60 * 1000  # 15分钟 * 每分钟60s
    elif time_interval.endswith('h'):
        time_segment = time_interval_int * 60 * 60 * 1000  # 2小时 * 每小时60分钟 * 每分钟60s

    since = now_milliseconds

    # cha = end - since
    # 循环获取历史数据
    all_kline_data = []
    while len(all_kline_data) < 1000:
        # kline_data = QA_fetch_okex_kline_with_auto_retry(symbol, since, '15m')
        kline_data = fetch_ohlcv(symbol, since, '15m')
        if kline_data:
            since = int(kline_data[-1][0])
            all_kline_data += kline_data

    # 对数据进行整理
    df = pd.DataFrame(all_kline_data, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + datetime.timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]

    # 删除重复的数据
    df.drop_duplicates(subset=['candle_begin_time_GMT8'], keep='last', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 为了保险起见，去掉最后一行最新的数据
    df = df[:-1]

    print(symbol, '获取历史数据行数：', len(df))
    return df