import json
import time

import requests
import datetime
import pandas as pd

from urllib.parse import urljoin

from dateutil.tz import tzutc

from QARealTrade.Function import cal_order_size, cal_order_price
from QAUilt.common import get_sign
from QAUilt.config import *


def futures_post_order(params):
    '''
     币币下单：
     POST /api/v5/trade/order
     body{"instId":"BTC-USDT","tdMode":"cash","clOrdId":"b15","side":"buy","ordType":"limit","px":"2.15","sz":"2"}
    '''
    requestPath = "/api/v5/trade/order"

    body = json.dumps(params)

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sign = get_sign((str(timestamp) + 'POST' + requestPath + body), secret)

    # 请求数据
    url = urljoin(
        OKEx_base_url,
        requestPath
    )

    headers = {"Content-Type": "application/json", "OK-ACCESS-KEY": apikey, "OK-ACCESS-SIGN": sign, "OK-ACCESS-TIMESTAMP": timestamp,
               "OK-ACCESS-PASSPHRASE": passwd}

    retries = 1
    while (retries != 0):
        try:

            req = requests.post(
                url,
                data=body,
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

def okex_future_place_order(symbol_info, symbol_config, symbol_signal, max_try_amount, symbol):

    # 下单参数
    params = {
        "instId": symbol_config[symbol]["instrument_id"],  # 合约代码
        "tdMode": "cross", #交易模式 保证金模式：isolated：逐仓 ；cross：全仓 非保证金模式：cash：非保证金
        # "ccy": "USDT",
        "ordType": "limit"
    }
    for order_type in symbol_signal[symbol]:
        if order_type == 1:
            params['side'] = 'buy'
            params['posSide'] = 'long'
        elif order_type == -1:
            params['side'] = 'sell'
            params['posSide'] = 'short'
        elif order_type == 0:
            params['side'] = 'sell'
            params['posSide'] = 'long'

        params['px'] = str(cal_order_price(symbol_info.at[symbol, "信号价格"], order_type))
        params['sz'] = str(cal_order_size(symbol, symbol_info, symbol_config[symbol]['leverage']))
        order_info = futures_post_order(params)
        print(order_info)

def single_threading_place_order(symbol_info, symbol_config, symbol_signal, max_try_amount=5):
    # 函数输出变量
    symbol_order = pd.DataFrame()

    # 如果有交易信号的话
    if symbol_signal:
        # 遍历有交易信号的交易对
        for symbol in symbol_signal.keys():
            # 下单
            _, order_id_list = okex_future_place_order(symbol_info, symbol_config, symbol_signal, max_try_amount, symbol)

            # 记录
            for order_id in order_id_list:
                symbol_order.loc[order_id, 'symbol'] = symbol
                # 从symbol_info记录下单相关信息
                symbol_order.loc[order_id, '信号价格'] = symbol_info.loc[symbol, '信号价格']
                symbol_order.loc[order_id, '信号时间'] = symbol_info.loc[symbol, '信号时间']

    return symbol_order