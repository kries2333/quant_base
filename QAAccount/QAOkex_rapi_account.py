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
    future_info = okex_futures_get_accounts()

    data = future_info[0]['details']
    df = pd.DataFrame(data, dtype=float).T  # 将数据转化为df格式
    return df

def fetch_future_position():
    data = okex_fetch_future_position()

    df = pd.DataFrame(data, dtype=float)

    return df


def update_symbol_info(symbol_info, symbol_config):
    # 通过交易所接口获取合约账户信息
    future_account = fetch_future_account()

    # 通过交易所接口获取合约账户持仓信息
    future_position = fetch_future_position()

    if future_account.empty is False:
        symbol_info['账户权益'] = future_account[0]['availEq']

    position = future_position.loc[0]
    if future_position.empty is False:
        # 从future_position中获取原始数据
        symbol_info['最大杠杆'] = position['lever']
        symbol_info['当前价格'] = position['last']
        symbol_info['多头持仓量'] = 0
        symbol_info['多头均价'] = 0
        symbol_info['多头收益率'] = 0
        symbol_info['多头收益'] = 0
        symbol_info['空头持仓量'] = 0
        symbol_info['空头均价'] = 0
        symbol_info['空头收益率'] = 0
        symbol_info['空头收益'] = 0

        if position['posSide'] == "long":
            symbol_info['多头持仓量'] = position['pos']
            symbol_info['多头均价'] = position['avgPx']
            symbol_info['多头收益率'] = position['uplRatio']
            symbol_info['多头收益'] = position['upl']
        elif future_position['posSide'] == "short":
            symbol_info['空头持仓量'] = position['pos']
            symbol_info['空头均价'] = position['avgPx']
            symbol_info['空头收益率'] = position['uplRatio']
            symbol_info['空头收益'] = position['upl']

    # 整理原始数据，计算需要的数据
    # 多头、空头的index
    long_index = symbol_info[symbol_info['多头持仓量'] > 0].index
    short_index = symbol_info[symbol_info['空头持仓量'] > 0].index
    # 账户持仓方向
    symbol_info.loc[long_index, '持仓方向'] = 1
    symbol_info.loc[short_index, '持仓方向'] = -1
    symbol_info['持仓方向'].fillna(value=0, inplace=True)
    # 账户持仓量
    symbol_info.loc[long_index, '持仓量'] = symbol_info['多头持仓量']
    symbol_info.loc[short_index, '持仓量'] = symbol_info['空头持仓量']
    # 持仓均价
    symbol_info.loc[long_index, '持仓均价'] = symbol_info['多头均价']
    symbol_info.loc[short_index, '持仓均价'] = symbol_info['空头均价']
    # 持仓收益率
    symbol_info.loc[long_index, '持仓收益率'] = symbol_info['多头收益率']
    symbol_info.loc[short_index, '持仓收益率'] = symbol_info['空头收益率']
    # 持仓收益
    symbol_info.loc[long_index, '持仓收益'] = symbol_info['多头收益']
    symbol_info.loc[short_index, '持仓收益'] = symbol_info['空头收益']
    # 删除不必要的列
    symbol_info.drop(['多头持仓量', '多头均价', '空头持仓量', '空头均价', '多头收益率', '空头收益率', '多头收益', '空头收益'],
                     axis=1, inplace=True)

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