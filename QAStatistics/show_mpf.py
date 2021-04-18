import mplfinance as mpf
import pandas as pd

import pyecharts.options as opts
from pyecharts.charts import Line, Kline, EffectScatter, Grid
from pyecharts.globals import ThemeType

symbol = 'ETH-USDT_5m'

def draw_chart(df):
    # temp = df[df['signal'].notnull()][['signal']]
    # temp = temp[temp['signal'] != temp['signal'].shift(1)]
    signal = df[df['signal'] == 1].values.tolist()
    high = df['high'].values.tolist()
    date = df['candle_begin_time'].values.tolist()

    new_data = df[['open', 'close', 'high', 'low']].values.tolist()
    line_upper_data = list(df['line_upper'].values)
    line_median_data = list(df['line_median'].values)
    line_lower_data = list(df['line_lower'].values)

    es = (
        EffectScatter()
        .add_xaxis(date)
        .add_yaxis("", signal)
    )

    kline = (
        Kline()
            .add_xaxis(xaxis_data=date)
            .add_yaxis("k_线图",
                       y_axis=new_data,
                       itemstyle_opts=opts.ItemStyleOpts(color="#ec0000",color0="#00da3c",border_color="#8A0000",border_color0="#008F28",),
                       markpoint_opts=opts.MarkPointOpts(
                           data=[
                               opts.MarkPointItem(type_="signal", name="signal")
                           ]
                       ),)
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        )

    )

    overlap_kline = kline.overlap(es)

    kline_line = (
        Line()
        .add_xaxis(xaxis_data=date)
            .add_yaxis(
            series_name="upper",
            y_axis=line_upper_data,
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            itemstyle_opts=opts.ItemStyleOpts(color="#0004a1"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="median",
            y_axis=line_median_data,
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            itemstyle_opts=opts.ItemStyleOpts(color="#fff401"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="lower",
            y_axis=line_lower_data,
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            itemstyle_opts=opts.ItemStyleOpts(color="#71f401"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )

    overlap_kline_line = kline_line.overlap(overlap_kline)

    # Kline And Line
    # overlap_kline_line = kline.overlap(line)
    # overlap_kline_line.render_notebook()
    # grid_chart = Grid(init_opts=opts.InitOpts(width="1400px", height="800px"))
    # grid_chart.add(
    #     overlap_kline_line,
    #     # 设置位置
    #     grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="2%", height="80%"),
    # )
    overlap_kline.render()

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
    draw_chart(df)