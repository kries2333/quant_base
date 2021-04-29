from flask import send_from_directory, render_template, request

import QAStrategy.Signals
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

    @app.route('/local')
    def local():
        symbol = 'ETH/USDT'
        signal_name = 'signal_double_bolling_mod1'
        rule_type = '15m'

        p = '../data/output/equity_curve/signal_double_bolling_mod1_ETH_15min_[440, 128].csv'
        _all_data = pd.read_csv(p)

        trade = transfer_equity_curve_to_trade(_all_data)
        print('逐笔交易：\n', trade)

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
                "message": "成功"
            }
        }
        return ret

