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

def binance_futures_get_accounts():

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

def binance_fetch_future_position():

    requestPath = "/api/v5/account/positions"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)

    # 请求数据
    url = urljoin(
        Binance_base_url,
        requestPath
    )

    headers = {"Content-Type": "application/json",
                "OK-ACCESS-KEY": apikey,
               "OK-ACCESS-SIGN": sign,
               "OK-ACCESS-TIMESTAMP": timestamp,
               "OK-ACCESS-PASSPHRASE": passwd}
    retries = 1
    while (retries != 0):
        try:

            req = requests.get(
                url,
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
            if msg_dict['code'] == '0':
                data = msg_dict['data']
                return data
            else:
                print("err=", req.content)

    return None