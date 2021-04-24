import json
import time

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin
from QAUilt.common import get_sign

OKEx_base_url = 'https://www.okex.com'

apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
passwd = "Tt84521485"
secret = "C07914C0F473535F92045FE10A4D6BEF"

account = {
    'balance': [
        {'总金额': ""}
    ]
}

def okex_futures_get_accounts():

    requestPath = "/api/v5/account/balance"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)

    # 请求数据
    url = urljoin(
        OKEx_base_url,
        requestPath
    )

    headers = {"OK-ACCESS-KEY": apikey,
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

    requestPath = "/api/v5/account/positions"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'GET' + requestPath), secret)

    # 请求数据
    url = urljoin(
        OKEx_base_url,
        requestPath
    )

    headers = {"OK-ACCESS-KEY": apikey,
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

# 暂时只支持okex
def fetch_future_account():
    data = okex_futures_get_accounts()

    symbol_info = dict()
    for v in data:
        details = v['details']
        for d in details:
            symbol_info['账户权益'] = d['eq']

    return symbol_info

def fetch_future_position():
    data = okex_fetch_future_position()

    symbol_position = dict()
    for v in data:
        symbol_position['最大杠杆'] = v['lever']
        symbol_position['开仓价格'] = v['avgPx']
        if v['posSide'] == "long":
            symbol_position['多头持仓量'] = v['pos']
            symbol_position['多头均价'] = v['avgPx']
            symbol_position['多头收益率'] = v['uplRatio']
            symbol_position['多头收益'] = v['upl']
        elif v['posSide'] == "short":
            symbol_position['空头持仓量'] = v['pos']
            symbol_position['空头均价'] = v['avgPx']
            symbol_position['空头收益率'] = v['uplRatio']
            symbol_position['空头收益'] = v['upl']

    return symbol_position


def update_symbol_info(symbol_info, symbol_config):
    future_account = fetch_future_account()

if __name__ == "__main__":
    # 通过交易所接口获取合约账户信息
    future_account = fetch_future_account()

    # 通过交易所接口获取合约账户持仓信息
    future_position = fetch_future_position()
    print(future_position)