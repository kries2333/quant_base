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
    print('111')

    @app.route('/')
    def index():
        # symbol = 'ETH/USDT'
        #
        # p = '../data/output/equity_curve/signal_double_bolling_mod1_ETH_15min_[440, 128].csv'
        # _all_data = pd.read_csv(p)
        #
        # _all_data = _all_data.sort_values(by='candle_begin_time', ascending=False)
        # last_time = _all_data.loc[0, 'candle_begin_time'] # 历史数据文件中，最近的一次时间
        # df = _all_data.copy()
        # df['candle_begin_time'] = df['candle_begin_time'].values.tolist()
        # df['volume'] = df['quote_volume']
        #
        # _df = df[['candle_begin_time', 'open', 'close', 'low', 'high']]
        # _df_boll = df[['upper', 'median', 'lower', 'volume']]
        # _df_list = np.array(_df).tolist()
        # _df_boll_list= np.array(_df_boll).transpose().tolist()
        # str_df_list = pformat(_df_list)
        # str_df_boll_list = pformat(_df_boll_list)
        #
        # if 'signal' in df.columns.tolist():
        #     x = list(df[df['signal'].notnull()]['candle_begin_time'])
        #     y = list(df[df['signal'].notnull()]['high'])
        #     z = list(df[df['signal'].notnull()]['signal'])
        #     signal = '['
        #     for i in zip(x,y,z):  #rgb(41,60,85)
        #         if i[2] ==1:
        #             temp = "{coord:['"+str(i[0])+"',"+str(i[1]) + "], label:{ normal: { formatter: function (param) { return \"买\";}} } ,itemStyle: {normal: {color: 'rgb(214,18,165)'}}},"
        #         elif i[2] ==-1:
        #             temp = "{coord:['" + str(i[0]) + "'," + str(
        #                 i[1]) + "] , label:{ normal: { formatter: function (param) { return \"卖\";}} } ,itemStyle: {normal: {color: 'rgb(0,0,255)'}}},"
        #         else:
        #             temp = "{coord:['" + str(i[0]) + "'," + str(
        #                 i[1]) + "], label:{ normal: { formatter: function (param) { return \"平仓\";}} },itemStyle: {normal: {color: 'rgb(224,136,11)'}}},"
        #
        #         signal += temp
        #     signal = signal.rstrip(',')
        #     signal += '],'
        #
        # _html = get_echarts_html(symbol, str_df_list, str_df_boll_list, signal)
        # return _html
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

        name = request.values.get("0")

        if name:
            if (straegy_start(name)):
                all_statistics(name)

        ret = {
            "code": 20000,
            "data": {
                "message": "成功"
            }
        }
        return ret

