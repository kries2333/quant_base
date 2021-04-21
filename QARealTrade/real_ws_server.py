import base64
import hmac
import json
import time

from hashlib import sha256
import websocket

"""
apikey = "ca34b533-4bd0-457a-bee7-b5a6eaf89da8"
secretkey = "C07914C0F473535F92045FE10A4D6BEF"
IP = "0"
备注名 = "kries_v5"
权限 = "只读/交易"
"""

privateUrl = 'wss://ws.okex.com:8443/ws/v5/private'

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

def on_open(ws):
    print('open')
    print(ws)

    # 连接成功后需要登录
    ws.send(loginData())


def on_message(ws, message):
    print('on_message')

    text = json.loads(message)
    if ('event' in text):
        op = text['event']
        code = text['code']
        if op == 'login' and code == '0':
            print("登录成功")
            ws.send(accoutData())
    else:
        print(text)


def on_error(ws, error):
    print('error')
    print(error)


def on_close(ws):
    print('close')
    print("### closed ###")


websocket.enableTrace(True)
ws = websocket.WebSocketApp(privateUrl,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()