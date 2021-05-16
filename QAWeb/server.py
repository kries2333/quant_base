# -*- coding: utf-8 -*-
import asyncio
import json
import time

from flask import Flask
import websockets
import pandas as pd
import numpy as np

from QAMarket.QAMarket import fetch_symbol_history_candle_data
from QAWeb.real_signals import real_signal_simple_bolling, real_signal_shanshan_bolling

ex = "binance"
symbol = "ETHUSDT"
time_interval = '15m'

def getCandleData():
    print('')
    valuas = []
    df = fetch_symbol_history_candle_data(ex, symbol, time_interval, 1000)

    signal, median, upper, lower, atr_upper, atr_lower = real_signal_shanshan_bolling(df, para=[400, 8])

    date = df['candle_begin_time'].astype('str', copy=False)

    for d in df.values:
        valuas.append([d[1], d[4], d[3], d[2]])

    median = median.fillna(0)
    upper = upper.fillna(0)
    lower = lower.fillna(0)
    atr_upper = atr_upper.fillna(0)
    atr_lower = atr_lower.fillna(0)
    return list(date), valuas, list(median), list(upper), list(lower), list(atr_upper), list(atr_lower)

async def handler(websocket, path):
    # while True:
        print("====循环发送数据====")
        date, valuas, median, upper, lower, atr_upper, atr_lower = getCandleData()

        msg = {
            'date': date,
            'values': valuas,
            'median': median,
            'upper': upper,
            'lower': lower,
            'atrUpper': atr_upper,
            'atrLower': atr_lower,
        }
        js = json.dumps(msg)
        await websocket.send(js)
        time.sleep(60)

if __name__ == '__main__':
    start_server = websockets.serve(handler, 'localhost', 8081)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

