import json
import time
import pandas as pd
import requests
from datetime import datetime, timedelta
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
            if msg_dict['code'] == '0':
                return msg_dict['data']
            else:
                print("err=", req.content)

    return None


# 获取历史数据
def fetch_okex_symbol_history_candle_data(symbol, time_interval, max_len):
    # 获取当前时间
    now_milliseconds = int(time.time() * 1e3)

    # # 每根K线的间隔时间
    # time_interval_int = int(time_interval[:-1])  # 若15m，则time_interval_int = 15；若2h，则time_interval_int = 2
    # if time_interval.endswith('m'):
    #     time_segment = time_interval_int * 60 * 1000  # 15分钟 * 每分钟60s
    # elif time_interval.endswith('h'):
    #     time_segment = time_interval_int * 60 * 60 * 1000  # 2小时 * 每小时60分钟 * 每分钟60s

    since = now_milliseconds

    # 循环获取历史数据
    all_kline_data = []
    while len(all_kline_data) < max_len:
        kline_data = fetch_ohlcv(symbol, since, time_interval)
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

def okex_fetch_candle_data(symbol, since=None, time_interval='1m', limit=100):
    data = fetch_ohlcv(symbol=symbol, timeframe=time_interval, limit=limit)
    # 整理数据
    df = pd.DataFrame(data, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high',
                       3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
    return df

# 获取需要的K线数据，并检测质量。
def get_candle_data(symbol_config, time_interval, run_time, max_try_amount, candle_num, symbol):
    # 标记开始时间
    start_time = datetime.now()
    print('开始获取K线数据：', symbol, '开始时间：', start_time)

    # 获取数据合约的相关参数
    instrument_id = symbol_config[symbol]["instrument_id"]  # 合约id
    signal_price = None

    # 尝试获取数据
    for i in range(max_try_amount):
        df = okex_fetch_candle_data(instrument_id, time_interval, limit=candle_num)
        if df.empty:
            continue  # 再次获取

        # 判断是否包含最新一根的K线数据。例如当time_interval为15分钟，run_time为14:15时，即判断当前获取到的数据中是否包含14:15这根K线
        # 【其实这段代码可以省略】
        if time_interval.endswith('m'):
            _ = df[df['candle_begin_time_GMT8'] == (run_time - timedelta(minutes=int(time_interval[:-1])))]
        elif time_interval.endswith('h'):
            _ = df[df['candle_begin_time_GMT8'] == (run_time - timedelta(hours=int(time_interval[:-1])))]
        else:
            print('time_interval不以m或者h结尾，出错，程序exit')
            exit()
        if _.empty:
            print('获取数据不包含最新的数据，重新获取')
            time.sleep(2)
            continue  # 再次获取

        else:  # 获取到了最新数据
            signal_price = df.iloc[-1]['close']  # 该品种的最新价格
            df = df[df['candle_begin_time_GMT8'] < pd.to_datetime(run_time)]  # 去除run_time周期的数据
            print('结束获取K线数据', symbol, '结束时间：', datetime.now())
            return symbol, df, signal_price

    print('获取candle_data数据次数超过max_try_amount，数据返回空值')
    return symbol, pd.DataFrame(), signal_price

def single_threading_get_data(symbol_info, symbol_config, time_interval, run_time, candle_num, max_try_amount=5):
    # 函数返回的变量
    symbol_candle_data = {}
    for symbol in symbol_config.keys():
        symbol_candle_data[symbol] = pd.DataFrame()

    # 逐个获取symbol对应的K线数据
    for symbol in symbol_config.keys():
        _, symbol_candle_data[symbol], symbol_info.at[symbol, '信号价格'] = get_candle_data(symbol_config, time_interval, run_time, max_try_amount, candle_num, symbol)

    return symbol_candle_data