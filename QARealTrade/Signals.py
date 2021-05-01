import pandas as pd
import random

# 将None作为信号返回
def real_signal_none(df, now_pos, avg_price, para):
    """
    发出空交易信号
    :param df:
    :param now_pos:
    :param avg_price:
    :param para:
    :return:
    """

    return None


# 随机生成交易信号
def real_signal_random(df, now_pos, avg_price, para):
    """
    随机发出交易信号
    :param df:
    :param now_pos:
    :param avg_price:
    :param para:
    :return:
    """

    r = random.random()
    if r <= 0.25:
        return 1
    elif r <= 0.5:
        return -1
    elif r <= 0.75:
        return 0
    else:
        return None


# 布林策略实盘交易信号
def real_signal_simple_bolling(df, now_pos, avg_price, para=[200, 2]):
    """
    实盘产生布林线策略信号的函数，和历史回测函数相比，计算速度更快。
    布林线中轨：n天收盘价的移动平均线
    布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
    当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
    :param df:  原始数据
    :param para:  参数，[n, m]
    :return:
    """

    # ===策略参数
    # n代表取平均线和标准差的参数
    # m代表标准差的倍数
    n = int(para[0])
    m = para[1]

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n).mean()  # 此处只计算最后几行的均线值，因为没有加min_period参数
    median = df.iloc[-1]['median']
    median2 = df.iloc[-2]['median']
    # 计算标准差
    df['std'] = df['close'].rolling(n).std(ddof=0)  # ddof代表标准差自由度，只计算最后几行的均线值，因为没有加min_period参数
    std = df.iloc[-1]['std']
    std2 = df.iloc[-2]['std']
    # 计算上轨、下轨道
    upper = median + m * std
    lower = median - m * std
    upper2 = median2 + m * std2
    lower2 = median2 - m * std2

    # ===寻找交易信号
    signal = None
    close = df.iloc[-1]['close']
    close2 = df.iloc[-2]['close']
    # 找出做多信号
    if (close > upper) and (close2 <= upper2):
        signal = 1
    # 找出做空信号
    elif (close < lower) and (close2 >= lower2):
        signal = -1
    # 找出做多平仓信号
    elif (close < median) and (close2 >= median2):
        signal = 0
    # 找出做空平仓信号
    elif (close > median) and (close2 <= median2):
        signal = 0

    p = "close={} upper={} close2={} upper2={}".format(close, upper, close2, upper2)
    print(p)
    print("signal", signal)
    return signal


def real_signal_simple_bolling_bias(df, now_pos, avg_price, para=[200, 0.3]):
    """
    实盘产生布林线策略信号的函数，和历史回测函数相比，计算速度更快。
    布林线中轨：n天收盘价的移动平均线
    布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
    当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
    :param df:  原始数据
    :param para:  参数，[n, m]
    :return:
    """

    # ===策略参数
    # n代表取平均线和标准差的参数
    # m代表标准差的倍数
    n = int(para[0])
    bias_pct = para[1]

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()  # 此处只计算最后几行的均线值，因为没有加min_period参数
    median = df.iloc[-1]['median']
    median2 = df.iloc[-2]['median']

    # 计算标准差
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度，只计算最后几行的均线值，因为没有加min_period参数
    std = df.iloc[-1]['std']
    std2 = df.iloc[-2]['std']

    z_score = abs((df['close'] - df['median']) / df['std'])
    m = z_score.rolling(window=n).max().shift(1).iloc[-1]

    # ===寻找交易信号
    signal = None
    close = df.iloc[-1]['close']
    close2 = df.iloc[-2]['close']

    print("平均线 n = ", n)
    print("标准差的倍数 m = ", m)

    # 计算上轨、下轨道
    upper = median + m * std
    lower = median - m * std
    upper2 = median2 + m * std2
    lower2 = median2 - m * std2

    # 计算bias
    bias = close / median - 1

    # 找出做多信号
    if (close > upper) and (close2 <= upper2) and (bias < bias_pct):
        signal = 1
    # 找出做空信号
    elif (close < lower) and (close2 >= lower2) and (bias > -1 * bias_pct):
        signal = -1
    # 找出做多平仓信号
    elif (close < median) and (close2 >= median2):
        signal = 0
    # 找出做空平仓信号
    elif (close > median) and (close2 <= median2):
        signal = 0

    p = "close={} upper={} close2={} upper2={} bias={}".format(close, upper, close2, upper2, bias)
    print(p)
    print("signal", signal)
    return signal


def real_signal_simple_bolling_bias1(df, now_pos, avg_price, para=[200, 2, 0.3]):
    """
     实盘产生布林线策略信号的函数，和历史回测函数相比，计算速度更快。
     布林线中轨：n天收盘价的移动平均线
     布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
     布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
     当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
     当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
     :param df:  原始数据
     :param para:  参数，[n, m]
     :return:
     """

    # ===策略参数
    # n代表取平均线和标准差的参数
    # m代表标准差的倍数
    n = int(para[0])
    m = para[1]
    bias_pct = para[2]

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()  # 此处只计算最后几行的均线值，因为没有加min_period参数
    median = df.iloc[-1]['median']
    median2 = df.iloc[-2]['median']

    # 计算标准差
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度，只计算最后几行的均线值，因为没有加min_period参数
    std = df.iloc[-1]['std']
    std2 = df.iloc[-2]['std']

    # ===寻找交易信号
    signal = None
    close = df.iloc[-1]['close']
    close2 = df.iloc[-2]['close']

    print("平均线 n = ", n)
    print("标准差的倍数 m = ", m)

    # 计算上轨、下轨道
    upper = median + m * std
    lower = median - m * std

    upper2 = median2 + m * std2
    lower2 = median2 - m * std2

    # 计算bias
    bias = close / median - 1

    # 计算价格偏离上下轨的比例
    bias_up = close / upper - 1
    bias_down = close / lower - 1

    # 找出做多信号
    if (close > upper) and (close2 <= upper2) and (bias < bias_pct):
        signal = 1
    # 找出做空信号
    elif (close < lower) and (close2 >= lower2) and (bias > -1 * bias_pct):
        signal = -1
    # 找出做多平仓信号
    elif (close < median) and (close2 >= median2) and (bias_up > bias_pct):
        signal = 0
    # 找出做空平仓信号
    elif (close > median) and (close2 <= median2) and (bias_down < -1 * bias_pct):
        signal = 0

    print("time={}".format(df.iloc[0]['candle_begin_time_GMT8']))
    print("close={} upper={} lower={}".format(close, upper, lower))
    print("close2={} upper2={} lower2={}".format(close2, upper2, lower2))
    print("signal={}  bias={} std={} std2={}".format(signal, bias, std, std2))
    return signal