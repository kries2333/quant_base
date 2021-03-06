import json
import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin

OKEx_base_url = 'https://www.okex.com'

def fetch_okex_ohlcv(symbol, since=None, timeframe='1m', limit=100):
    # 请求数据
    url = urljoin(
        OKEx_base_url,
        '/api/v5/market/candles'
    )

    if (since == None):
        params = {
            "instId": symbol,
            "bar": timeframe,
            "limit": limit
        }
    else:
        params = {
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