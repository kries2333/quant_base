import json
import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin

Binance_base_url = 'https://fapi.binance.com'

def fetch_binance_ohlcv(symbol, timeframe, limit=100):
    # 请求数据
    url = urljoin(
        Binance_base_url,
        '/fapi/v1/klines'
    )

    params = {
        "symbol": symbol,
        "interval": timeframe,  # Z结尾的ISO时间 String
        "limit": 1000
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
            return msg_dict

    return None