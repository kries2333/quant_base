import json

from flask import send_from_directory, render_template, request

import QAStrategy.Signals
from QAAccount.QAAccount_binance import binance_futures_get_accounts, binance_fetch_future_position
from QAStatistics.all_bolling_statistics import all_statistics
from QAStrategy.Statistics import transfer_equity_curve_to_trade
from QAStrategy.strategy_params import straegy_start
from echarts_data import get_echarts_html, gen_echarts_data
import pandas as pd
import numpy as np
from pprint import pprint, pformat


def routes(app):
    @app.route('/')
    def index():
        print("index")

    @app.route('/get_cash_data')
    def getCashData():
        data = []

        try:
            info = binance_futures_get_accounts()

            for k in range(len(info)):
                d = dict()
                d['asset'] = info[k]['asset']
                d['balance'] = info[k]['balance']
                d['cross'] = info[k]['crossUnPnl']
                d['available'] = info[k]['availableBalance']
                d['ex'] = "BINANCE"
                data.append(d)
        except Exception as err:
            print(err)

        res = {
            'data': data
        }
        return json.dumps(res)

    @app.route('/get_position_data')
    def getPositionData():

        data = []

        try:
            info = binance_fetch_future_position()

            positions = info['positions']

            for k in range(len(positions)):
                amt = float(positions[k]['positionAmt'])
                if amt > 0:
                    d = dict()
                    d['symbol'] = positions[k]['symbol']
                    d['ex'] = "BINANCE"
                    d['leverage'] = positions[k]['leverage']
                    d['side'] = positions[k]['positionSide']
                    d['amt'] = positions[k]['positionAmt']
                    d['unprofit'] = positions[k]['unrealizedProfit']
                    data.append(d)
        except Exception as err:
            print(err)

        res = {
            'data': data
        }
        return json.dumps(res)

    @app.route('/local')
    def local():
        symbol = 'ETH/USDT'
        signal_name = 'signal_double_bolling_rsi'
        rule_type = '15m'

        p = '../data/output/equity_curve/signal_double_bolling_rsi_ETH_15T_[180].csv'
        _all_data = pd.read_csv(p)

        trade = transfer_equity_curve_to_trade(_all_data)
        print('???????????????\n', trade)

        gen_echarts_data(_all_data, trade, signal_name, symbol, rule_type)

        return app.send_static_file('html/strategy_signals_viewer.html')

    @app.route('/strategy/start')
    def start():

        model = request.values["model"]
        name = request.values["name"]
        if name:
            if (straegy_start(model, name)):
                all_statistics(name)

        ret = {
            "code": 20000,
            "data": {
                "message": "??????"
            }
        }
        return ret
