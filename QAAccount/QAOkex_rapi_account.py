import json
import time

import requests
import datetime

from urllib.parse import urljoin
from QAUilt.common import get_sign

OKEx_base_url = 'https://www.okex.com'

apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
passwd = "Tt84521485"

account = {
    'balance': [
        {'总金额': ""}
    ]
}

def okex_futures_get_accounts():

    requestPath = "/api/v5/account/balance"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    secret = "C07914C0F473535F92045FE10A4D6BEF"
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
    for v in data:
        details = v['details']
        for d in details:
            print(d['totalEq'])

def update_symbol_info(symbol_info, symbol_config):
    print("")

if __name__ == "__main__":
    data = fetch_future_account()
    print(data)