import hmac
import json
import time
from _sha256 import sha256

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin
from QAUilt.common import get_sign

Binance_base_url = 'https://fapi.binance.com'

apikey = "j4MI0GEdLGS6Aa6MlhuuBZqtGJBbSQRTVQuBKC9enPtGEGfol67jMFIi9Hkudno4"
secret = "gWSDCYJxQQKo174FEHvxTkzTcxFyzK4mlqXa3s13yslttRrZfkHnWgDoDNndZB1R"

def get_SHA256(data, key):
    data = data.encode('utf-8')
    sign = hmac.new(key.encode('utf-8'), data, digestmod=sha256).hexdigest().upper()
    return sign

def get_futures_get_accounts():

    requestPath = "/fapi/v2/balance"

    timestamp = int(round(time.time() * 1000))

    # 请求数据
    url = urljoin(
        Binance_base_url,
        requestPath
    )

    headers = {"Content-Type": "application/json",
               "X-MBX-APIKEY": apikey}



    sign = get_SHA256('timestamp=' + (str(timestamp)), secret)
    params = {
        'timestamp': timestamp,
        'signature': sign
    }

    retries = 1
    while (retries != 0):
        try:

            req = requests.get(
                url,
                params=params,
                headers=headers
            )
            # 防止频率过快
            time.sleep(0.5)
            retries = 0
        except (ConnectionError):
            retries = 1

        if (retries == 0):
            # 成功获取才处理数据，否则继续尝试连接
            msg_dict = json.loads(req.content)
            return msg_dict

    return None

def binance_futures_get_accounts():
    future_info = get_futures_get_accounts()
    df = pd.DataFrame(future_info, dtype=float).T  # 将数据转化为df格式\
    df['账户权益'] = future_info[1]['balance']

    return df

def get_fetch_future_position():
    requestPath = "/fapi/v2/account"

    timestamp = int(round(time.time() * 1000))

    # 请求数据
    url = urljoin(
        Binance_base_url,
        requestPath
    )

    headers = {"Content-Type": "application/json",
               "X-MBX-APIKEY": apikey}

    sign = get_SHA256('timestamp=' + (str(timestamp)), secret)
    params = {
        'timestamp': timestamp,
        'signature': sign
    }

    retries = 1
    while (retries != 0):
        try:

            req = requests.get(
                url,
                params=params,
                headers=headers
            )
            # 防止频率过快
            time.sleep(0.5)
            retries = 0
        except (ConnectionError):
            retries = 1

        if (retries == 0):
            # 成功获取才处理数据，否则继续尝试连接
            msg_dict = json.loads(req.content)
            return msg_dict['positions']

    return None

def binance_fetch_future_position():

    position_info = get_fetch_future_position()

    # 整理数据
    df = pd.DataFrame(position_info, dtype=float)

    # 防止账户初始化时出错
    if "symbol" in df.columns:
        df['index'] = df['symbol']
        df.set_index(keys='index', inplace=True)
        df.index.name = None
    return df