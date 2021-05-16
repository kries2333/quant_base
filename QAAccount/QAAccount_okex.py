import json
import time

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin
from QAUilt.common import get_sign

apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
passwd = "Tt84521485"
secret = "C07914C0F473535F92045FE10A4D6BEF"

OKEx_base_url = 'https://www.okex.com'

def get_futures_get_accounts():

    requestPath = "/api/v5/account/balance"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)

    # 请求数据
    url = urljoin(
        OKEx_base_url,
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
                return data[0]['details']
            else:
                print("err=", req.content)

    return None

def okex_futures_get_accounts():
    future_info = get_futures_get_accounts()

    data = future_info[0]['details']
    df = pd.DataFrame(data, dtype=float).T  # 将数据转化为df格式
    return df

def get_fetch_future_position():
    requestPath = "/api/v5/account/positions"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)

    # 请求数据
    url = urljoin(
        OKEx_base_url,
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

def okex_fetch_future_position():
    position_info = get_fetch_future_position()
    # 整理数据
    df = pd.DataFrame(position_info, dtype=float)

    # 防止账户初始化时出错
    if "instId" in df.columns:
        df['index'] = df['instId'].str[:-5].str.lower()
        df.set_index(keys='index', inplace=True)
        df.index.name = None
    return df