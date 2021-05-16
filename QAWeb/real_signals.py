# 布林策略实盘交易信号
import numpy as np
import talib


def real_signal_simple_bolling(df, para=[200, 2]):
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

    upper_list = df['median'] + m * df['std']
    lower_list = df['median'] - m * df['std']

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
    return signal, df['median'], upper_list, lower_list

# 闪闪的策略
def real_signal_shanshan_bolling(df, para=[200, 2]):
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
    bolling_window = int(para[0])
    d = para[1]

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(bolling_window).mean()  # 此处只计算最后几行的均线值，因为没有加min_period参数
    median = df.iloc[-1]['median']
    median2 = df.iloc[-2]['median']

    # 计算标准差
    df['std'] = df['close'].rolling(bolling_window).std(ddof=0)  # ddof代表标准差自由度，只计算最后几行的均线值，因为没有加min_period参数
    std = df.iloc[-1]['std']
    std2 = df.iloc[-2]['std']

    m = (abs((df['close'] - df['median']) / df['std'])).rolling(bolling_window, min_periods=1).max()
    # 计算上轨、下轨道
    upper = median + m.iloc[-1] * std
    lower = median - m.iloc[-1] * std
    upper2 = median2 + m.iloc[-2] * std2
    lower2 = median2 - m.iloc[-2] * std2

    upper_list = df['median'] + m * df['std']
    lower_list = df['median'] - m * df['std']

    # ===计算KDJ指标
    df['k'], df['d'] = np.float16(talib.STOCH(high = df['high'], low = df['low'], close = df['close'],
                                #此处三个周期(9,3,3)只是习惯取法可以作为参数更改
                                fastk_period = 9, # RSV值周期
                                slowk_period = 3, # 'K'线周期
                                slowd_period = 3, # 'D'线周期
                                slowk_matype = 1,  # 'K'线平滑方式，1为指数加权平均，0 为普通平均
                                slowd_matype = 1))# 'D'线平滑方式，1为指数加权平均，0 为普通平均
    df['j'] = df['k'] * 3 - df['d'] * 2   # 'J' 线

    # 计算j值在kdj_window下的历史百分位
    kdj_window = 9 # 此处的回溯周期取为上面计算kdj的fastk_period
    j_max = df['j'].rolling(kdj_window, min_periods=1).max()
    j_min = df['j'].rolling(kdj_window, min_periods=1).min()
    df['j_exceed'] = abs(j_max - df['j']) / abs(j_max - j_min)
    j_exceed = df.iloc[-1]['j_exceed']

    # 计算ATR
    df['atr'] = talib.ATR(high=df['high'],low=df['low'],close=df['close'],timeperiod=int(bolling_window/d))

    # 计算ATR布林通道上下轨
    df['atr_upper'] = df['median'] + df['atr']
    df['atr_lower'] = df['median'] - df['atr']

    atr_upper = df.iloc[-1]['atr_upper']
    atr_lower = df.iloc[-1]['atr_lower']

    # ===寻找交易信号
    signal = None
    close = df.iloc[-1]['close']
    close2 = df.iloc[-2]['close']
    # 找出做多信号
    if (close > upper) and (close2 <= upper2) and (j_exceed <= 0.3) and (close >= atr_upper):
        signal = 1
    # 找出做空信号
    elif (close < lower) and (close2 >= lower2) and (j_exceed >= 0.7) and (close <= atr_lower):
        signal = -1
    # 找出做多平仓信号
    elif (close < median) and (close2 >= median2):
        signal = 0
    # 找出做空平仓信号
    elif (close > median) and (close2 <= median2):
        signal = 0

    return signal, df['median'], upper_list, lower_list, df['atr_upper'], df['atr_lower']