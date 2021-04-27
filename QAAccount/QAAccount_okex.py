import json
import time

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin
from QAUilt.common import get_sign
from QAUilt.config import *


def okex_futures_get_accounts():

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

# 暂时只支持okex
def fetch_future_account():
    future_info = okex_futures_get_accounts()

    data = future_info[0]['details']
    df = pd.DataFrame(data, dtype=float).T  # 将数据转化为df格式
    return df

def fetch_future_position():

    position_info = okex_fetch_future_position()
    # 整理数据
    df = pd.DataFrame(position_info, dtype=float)
    # 防止账户初始化时出错
    if "instId" in df.columns:
        df['index'] = df['instId'].str[:-5].str.lower()
        df.set_index(keys='index', inplace=True)
        df.index.name = None
    return df

def update_symbol_info(symbol_info, symbol_config):
    # 通过交易所接口获取合约账户信息
    future_account = fetch_future_account()

    # 通过交易所接口获取合约账户持仓信息
    future_position = fetch_future_position()

    if future_account.empty is False:
        symbol_info['账户权益'] = future_account[0]['availEq']

    if future_position.empty is False:
        for x in future_position.index:
            position = future_position.loc[x]
            instrument_id = x.upper()
            # 从future_position中获取原始数据
            symbol_info.loc[instrument_id, '最大杠杆'] = position['lever']
            symbol_info.loc[instrument_id, '当前价格'] = position['last']

            if position['posSide'] == "long":
                symbol_info.loc[instrument_id, '持仓方向'] = '多单'
                symbol_info.loc[instrument_id, '持仓量'] = position['pos']
                symbol_info.loc[instrument_id, '持仓均价'] = position['avgPx']
                symbol_info.loc[instrument_id, '持仓收益率'] = position['uplRatio']
                symbol_info.loc[instrument_id, '持仓收益'] = position['upl']
            elif position['posSide'] == "short":
                symbol_info.loc[instrument_id, '持仓方向'] = '空单'
                symbol_info.loc[instrument_id, '持仓量'] = position['pos']
                symbol_info.loc[instrument_id, '持仓均价'] = position['avgPx']
                symbol_info.loc[instrument_id, '持仓收益率'] = position['uplRatio']
                symbol_info.loc[instrument_id, '持仓收益'] = position['upl']

    else:
        # 当future_position为空时，将持仓方向的控制填充为0，防止之后判定信号时出错
        symbol_info['持仓方向'].fillna(value=0, inplace=True)

    return symbol_info

if __name__ == "__main__":
    pass
    # # =获取持仓数据
    # # 初始化symbol_info，在每次循环开始时都初始化
    # symbol_info_columns = ['账户权益', '持仓方向', '持仓量', '持仓收益率', '持仓收益', '持仓均价', '当前价格', '最大杠杆']
    # symbol_info = pd.DataFrame(index=symbol_config.keys(), columns=symbol_info_columns)  # 转化为dataframe
    #
    # # 通过交易所接口获取合约账户信息
    # symbol_info = update_symbol_info()
    # print(symbol_info)