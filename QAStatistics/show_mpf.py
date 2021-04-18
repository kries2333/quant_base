import mplfinance as mpf
import pandas as pd

import pyecharts.options as opts
from pyecharts.charts import Line, Kline, Grid

symbol = 'ETH-USDT_5m'

def show(df):

    # curve_x = df['candle_begin_time'].values.tolist()
    # curve_y = df['open'].round(2).values.tolist()

    # c = (
    #     Line().add_xaxis(curve_x).add_yaxis("收益曲线 %s" % symbol, curve_y,
    #                                         areastyle_opts=opts.AreaStyleOpts(opacity=0.5)).set_global_opts(
    #         title_opts=opts.TitleOpts(title='策略收益曲线图')).render("line_area_style.html")
    # )

    date = df["candle_begin_time"].apply(lambda x: str(x)).tolist()
    k_plot_value = df.apply(lambda record: [record['open'], record['close'], record['low'], record['high']],
                            axis=1).tolist()
    sig_value = df.apply(lambda record: [record['sig_short']],
                            axis=1).tolist()


    kline = Kline()
    kline.add_xaxis(date)
    kline.add_yaxis("kline", k_plot_value, markpoint_opts=sig_value)
    kline.set_global_opts(yaxis_opts=opts.AxisOpts(is_scale=True),
            xaxis_opts=opts.AxisOpts(is_scale=True),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")])

    lines = Line()
    lines.add_xaxis(date)
    lines.add_yaxis("sig", sig_value)

    overlap_1 = lines.overlap(kline)
    grid = Grid(init_opts=opts.InitOpts(width="1000px", height="800px"))
    grid.add(overlap_1, grid_opts=opts.GridOpts(pos_right="58%"), is_control_axis_index=True)
    grid.render()

if __name__ == "__main__":
    # =====读入数据
    df = pd.read_csv('../data/output/equity_curve/signal_simple_bolling_ETH_1h_[100, 3.5].csv')

    title = '单一策略数据显示'

    color = mpf.make_marketcolors(up='g', down='r', edge='inherit')
    style = mpf.make_mpf_style(marketcolors=color)

    # 创建开平仓信号的作图数据
    df['sig_long'] = df.loc[df['signal'] == 1, 'close']
    df['sig_short'] = df.loc[df['signal'] == -1, 'close']
    df['sig_close'] = df.loc[df['signal'] == 0, 'close']
    # 按mplfinance要求修改列名
    df['Date'] = pd.to_datetime(df['candle_begin_time'])
    df.set_index('Date', inplace=True)
    df['Open'] = df['open']
    df['High'] = df['high']
    df['Low'] = df['low']
    df['Close'] = df['close']
    df['Volume'] = df['b_bar_quote_volume']

    # # 选取要画图的列
    # df = df[['Open', 'High', 'Low', 'Close', 'Volume',
    #          # 'quote_volume',
    #          'line_upper', 'line_median', 'line_lower',
    #          # 'K','D','J',
    #          'sig_long', 'sig_short', 'sig_close',
    #          'r_line_equity_curve',
    #          ]]

    # # 截取最大回撤部分
    # df = df['2019-06-26 20:30:00':'2019-10-25 21:30:00']
    #
    # add_plot = [
    #     mpf.make_addplot(df['line_upper'], linestyle='dotted', panel=0),
    #     mpf.make_addplot(df['line_median'], linestyle='dotted', panel=0),
    #     mpf.make_addplot(df['line_lower'], linestyle='dotted', panel=0),
    #     # mpf.make_addplot(df['K'], linestyle='dotted', panel=1,color = 'blue'),
    #     # mpf.make_addplot(df['D'], linestyle='dotted', panel=1,color = 'yellow'),
    #     # mpf.make_addplot(df['J'], linestyle='dotted', panel=1,color = 'black'),
    #     mpf.make_addplot(df['sig_short'], type='scatter', panel=0, markersize=100, marker='v', color='r'),
    #     mpf.make_addplot(df['sig_long'], type='scatter', panel=0, markersize=100, marker='^', color='g'),
    #     mpf.make_addplot(df['sig_close'], type='scatter', panel=0, markersize=100, color='orange'),
    #     # mpf.make_addplot(df['r_line_equity_curve'], color='purple', panel=0)
    #     # mpf.make_addplot(df['rsi'],color='b',panel=0)
    # ]
    show(df)