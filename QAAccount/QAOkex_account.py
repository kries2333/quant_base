import json
import time
from hashlib import sha256

import websocket
import base64
import hmac


def get_sign(data, key):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    sign = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest())
    sign = str(sign, 'utf-8')
    print(sign)
    return sign

def loginData():
    timestamp = time.time()
    secret = "C07914C0F473535F92045FE10A4D6BEF"
    sign = get_sign((str(timestamp) + 'GET' + '/users/self/verify'), secret)

    sendData = {
        "op": 'login',
        "args": [
            {
                "apiKey": "ca34b533-4bd0-457a-bee7-b5a6eaf89da8",
                "passphrase": "Tt84521485",
                "timestamp": str(timestamp),
                "sign": sign
            }
        ]
    }

    return json.dumps(sendData)


def accoutData():
    sendData = {
        "op": 'subscribe',
        "args": [
            {
                "channel": "account"
            }
        ]
    }

    return json.dumps(sendData)


"""
apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
secretkey = "C07914C0F473535F92045FE10A4D6BEF"
IP = "0"
备注名 = "kries_v5"
权限 = "只读/交易"
"""

class QAAccount:
    def __init__(self):
        self.privateUrl = "wss://ws.okex.com:8443/ws/v5/private"
        self.apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
        self.secretkey = "C07914C0F473535F92045FE10A4D6BEF"
        self.passphrase = "Tt84521485"
        self.account_info = []

    def onOpen(self, ws):
        print(ws)
        ws.send(loginData())

    def onMessage(self, ws, message):
        print('message')

        text = json.loads(message)
        if ('event' in text) and ('code' in text):
            op = text['event']
            code = text['code']
            if op == 'login' and code == '0':
                print("登录成功")
                ws.send(accoutData())
        else:
            self.account_info = text['data']
            print(text)

    def onError(self, ws, error):
        print('error')

    def onClose(self, ws):
        print('close')


    def start(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.privateUrl,
                                    on_open=self.onOpen,
                                    on_message=self.onMessage,
                                    on_error=self.onError,
                                    on_close=self.onClose)

        ws.run_forever()