import json
import time

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin
from QAUilt.common import get_sign

Binance_base_url = 'https://fapi.binance.com'

apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
passwd = "Tt84521485"
secret = "C07914C0F473535F92045FE10A4D6BEF"

def binance_futures_get_accounts():

    requestPath = "/fapi/v2/balance"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)



    # 请求数据
    url = urljoin(
        Binance_base_url,
        requestPath
    )

    headers = {"Content-Type": "application/json",
               "X-MBX-APIKEY": apikey}

    params = {
        'timestamp': timestamp,
        'signature': ''
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
                data = msg_dict['data']
                return data
            else:
                print("err=", req.content)

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