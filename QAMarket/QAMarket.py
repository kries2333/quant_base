import json

import requests
import pandas as pd
import time
from urllib.parse import urljoin

OKEx_base_url = 'https://www.okex.com'


def fetch_okex_symbol_candle_data(symbol):
    # 请求数据
    url = urljoin(
        OKEx_base_url,
        '/api/v5/market/history-candles'
    )

    time_inla = int(time.time() * 1000)
    retries = 1
    while (retries != 0):
        try:
            req = requests.get(
                url,
                params={
                    "instId": symbol,
                    "after": time_inla,  # Z结尾的ISO时间 String
                    "bar": "15m"
                },
            )
            # 防止频率过快
            time.sleep(0.5)
            retries = 0
        except (ConnectionError):
            retries = 1

        if (retries == 0):
            # 成功获取才处理数据，否则继续尝试连接
            msg_dict = json.loads(req.content)


if __name__ == "__main__":
    fetch_okex_symbol_candle_data('ETH-USDT-210423')