import json
import time
import traceback

import requests
from _datetime import datetime
import pandas as pd

from urllib.parse import urljoin

from dateutil.tz import tzutc

from QARealTrade.Function import cal_order_size, cal_order_price
from QAUilt.common import get_sign

OKEx_base_url = 'https://www.okex.com'

apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
passwd = "Tt84521485"
secret = "C07914C0F473535F92045FE10A4D6BEF"

def futures_post_order(params):
    '''
     币币下单：
     POST /api/v5/trade/order
     body{"instId":"BTC-USDT","tdMode":"cash","clOrdId":"b15","side":"buy","ordType":"limit","px":"2.15","sz":"2"}
    '''
    requestPath = "/api/v5/trade/order"

    body = json.dumps(params)

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
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
        "ccy": "USDT",
        "ordType": "limit"
    }

    order_id_list = []
    for order_type in symbol_signal[symbol]:

        params['px'] = str(cal_order_price(symbol_info.at[symbol, "信号价格"], order_type))
        params['sz'] = str(int(cal_order_size(symbol, symbol_info, symbol_config[symbol]['leverage'])))
        try:
            if order_type == 1:
                params['side'] = 'buy'
                params['posSide'] = 'long'
            elif order_type == 2:
                params['side'] = 'sell'
                params['posSide'] = 'short'
            elif order_type == 3:
                params['side'] = 'sell'
                params['posSide'] = 'long'
            elif order_type == 4:
                params['side'] = 'buy'
                params['posSide'] = 'short'
            if order_type in [1, 4]:    # 开多并平空
                params['side'] = 'buy'
                params['posSide'] = 'long'
            elif order_type in [2, 3]: # 开空并平多
                params['side'] = 'buy'
                params['posSide'] = 'short'


            print('开始下单：', datetime.now())
            # order_info = futures_post_order(params)
            # for order in order_info:
            #     order_id_list.append(order['ordId'])
            # print(order_info, '下单完成：', datetime.now())
        except Exception as e:
            print(e)
            print("下单失败")
            traceback.print_exc()

    return order_id_list

def single_threading_place_order(symbol_info, symbol_config, symbol_signal, max_try_amount=5):
    # 函数输出变量
    symbol_order = pd.DataFrame()

    # 如果有交易信号的话
    if symbol_signal:
        # 遍历有交易信号的交易对
        for symbol in symbol_signal.keys():
            # 下单
            order_id_list = okex_future_place_order(symbol_info, symbol_config, symbol_signal, max_try_amount, symbol)

            # 记录
            for order_id in order_id_list:
                symbol_order.loc[order_id, 'symbol'] = symbol
                # 从symbol_info记录下单相关信息
                symbol_order.loc[order_id, '信号价格'] = symbol_info.loc[symbol, '信号价格']
                symbol_order.loc[order_id, '信号时间'] = symbol_info.loc[symbol, '信号时间']

    return symbol_order