import numpy as np
import pandas as pd
# 布林+bias策略自适应参数1
import talib


def signal_double_bolling_mod1(df, para=[200, 20]):
    """
    :param df:
    :param para: n, m
    :return:
    # 双均线,基础模型
    # 布林线策略
    # 布林线中轨：n天收盘价的移动平均线
    # 布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    # 布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    # 当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
    # 当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
    """

    # ===策略参数
    n1 = int(para[0])
    n2 = int(para[1])

    median1 = df['close'].rolling(n1, min_periods=1).mean()
    median2 = df['close'].rolling(n2, min_periods=1).mean()

    std1 = df['close'].rolling(n1, min_periods=1).std(ddof=0)
    std2 = df['close'].rolling(n2, min_periods=1).std(ddof=0)

    z_score = abs((df['close'] - median1) / std1)
    m1 = z_score.rolling(window=n1).max().shift(1)

    z_score = abs((df['close'] - median2) / std2)
    m2 = z_score.rolling(window=n2).max().shift(1)

    upper1 = median1 + m1 * std1
    lower1 = median1 - m1 * std1

    upper2 = median2 + m2 * std2
    lower2 = median2 - m2 * std2

    condition1 = lower2 > median1
    condition2 = lower2.shift(1) <= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多


    # # 找出做多平仓信号
    condition1 = upper2 > median1
    condition2 = upper2.shift(1) <= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = upper2 > median1
    condition2 = upper2.shift(1) <= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition1 = lower2 > median1
    condition2 = lower2.shift(1) <= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']

    df['upper'] = upper1
    df['lower'] = lower1
    df['median'] = median1

    # ===删除无关变量
    df.drop(['signal_long', 'signal_short'], axis=1, inplace=True)

    return df

def signal_double_bolling_mod1_para_list(m_list=range(200, 500, 10), n_list=range(10, 200, 2)):
    """
        :param m_list:
        :param n_list:
        :param bias_pct_list:
        :param stoploss_pct_list:
        :return:
        """
    """
     产生布林 策略的参数范围
     :param m_list:
     :param n_list:
     :return:
     """
    para_list = []

    for m in m_list:
        for n in n_list:
            para = [m, n]
            para_list.append(para)

    return para_list

def signal_atrboll_bolling(df, para=[200, 10]):
    """
    :param df:
    :param para: n, m
    :return:

    # 布林线策略
    # 布林线中轨：n天收盘价的移动平均线
    # 布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    # 布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    # 当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
    # 当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
    """

    # ===策略参数
    bolling_window = int(para[0])
    d = float(para[1])

    # ===计算布林指标
    # 计算均线 、上轨、下轨
    df['median'] = df['close'].rolling(bolling_window,min_periods=1).mean()
    df['std'] = df['close'].rolling(bolling_window,min_periods=1).std(ddof=0)  # ddof代表标准差自由度
    # 自适应改造 bolling_std系数 m
    df['m'] = (abs((df['close']-df['median'])/df['std'])).rolling(bolling_window,min_periods=1).max()
    df['upper'] = df['median'] + df['m'] * df['std']
    df['lower'] = df['median'] - df['m'] * df['std']


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

    # 计算ATR
    df['atr'] = talib.ATR(high=df['high'],low=df['low'],close=df['close'],timeperiod=int(bolling_window * d))
    # 增加平均数过滤条件（此方法未达标）
    df['atr_std'] = df['atr'].rolling(window=int(bolling_window/d - 1),min_periods=1).std() # atr的波动程度（范围）
    df['atr_max'] = df['atr'].rolling(window=int(bolling_window/d - 1),min_periods=1).max()
    df['atr_min'] = df['atr'].rolling(window=int(bolling_window/d - 1),min_periods=1).min()
    df['atr_mid'] = (df['atr_max']+df['atr_min'])/2  # 取最大最小平均数
    atr_condition = abs(df['atr'] - df['atr_mid']) <= df['atr_std']


    # 计算ATR布林通道上下轨
    df['atr_upper'] = df['median'] + df['atr']
    df['atr_lower'] = df['median'] - df['atr']



    # ===计算信号
    # 找出做多信号
    condition_long = (df['close'] >= df['upper']) & (df['close'].shift(1) <= df['upper'].shift(1))  # K线上穿上轨
    kdj_limit = df['j_exceed'] <= 0.2  # 判断 j值的历史百分位低于30%为超卖，可以做多
    # condition3 = df['close'] >= df['atr_upper']
    condition3 = atr_condition
    df.loc[condition_long & kdj_limit & condition3, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多
    # 找出做多平仓信号，
    condition_sell = (df['close'] < df['median']) & (df['close'].shift(1) >= df['median'].shift(1))  # k线下穿中轨
    df.loc[condition_sell, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    # 找出做空信号
    condition_short = (df['close'] <= df['lower']) & (df['close'].shift(1) >= df['lower'].shift(1))  # 当前K线下穿下轨
    kdj_limit = df['j_exceed'] >= 0.8  # 判断 j值的历史百分位高于于70%为超卖，可以做空
    condition3 = df['close'] <= df['atr_lower']
    df.loc[condition_short & kdj_limit & condition3, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空
    # 找出做空平仓信号
    condition_cover = (df['close'] > df['median']) & (df['close'].shift(1) <= df['median'].shift(1))  # K线上穿中轨
    df.loc[condition_cover, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # # 合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']

    # ===删除无关变量
    df.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short'], axis=1, inplace=True)
    # df.drop(['std', 'signal_long', 'signal_short','m','kdj_exceed'], axis=1, inplace=True)
    return df

def signal_atrboll_bolling_para_list(m_list=range(20, 1000+20, 20), d_list=[i / 10 for i in list(np.arange(1, 100, 2))]):

    print('参数遍历范围：')
    print('boll_window', list(m_list))
    print('d', list(d_list))
    print('参数空间:', len(list(m_list)) * len(list(d_list)))
    para_list = []
    for m in m_list:
        for d in d_list:
            para = [m, d]
            para_list.append(para)
    return para_list

def signal_double_bolling_rsi(df, para=[20, 200]):
    """
     :param df:
     :param para: n, m
     :return:

     # 布林线策略
     # 布林线中轨：n天收盘价的移动平均线
     # 布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
     # 布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
     # 当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
     # 当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
     """

    # ===策略参数
    n = int(para[0])
    m = float(para[1])

    # ===计算布林指标
    # 计算均线 、上轨、下轨
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度

    # 自适应改造 bolling_std系数 m
    df['m'] = (abs((df['close'] - df['median']) / df['std'])).rolling(n, min_periods=1).max()
    df['upper'] = df['median'] + df['m'] * df['std']
    df['lower'] = df['median'] - df['m'] * df['std']

    # ===计算RSI指标
    rsi = talib.RSI(df['close'], m)

    # ===计算信号
    # 找出做多信号
    # condition_long = (df['close'] >= df['upper']) & (df['close'].shift(1) <= df['upper'].shift(1))  # K线上穿上轨
    condition1 = df['close'] > df['median'] & df['close'] < df['upper']
    rsi_limit = rsi > 50
    df.loc[condition1 & rsi_limit, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 找出做多平仓信号，
    condition_sell = (df['close'] < df['median']) & (df['close'].shift(1) >= df['median'].shift(1))  # k线下穿中轨
    rsi_limit = rsi > 80  # 判断 j值的历史百分位低于30%为超卖，可以做多
    df.loc[rsi_limit, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    # condition_short = (df['close'] <= df['lower']) & (df['close'].shift(1) >= df['lower'].shift(1))  # 当前K线下穿下轨
    condition1 = df['close'] < df['median'] & df['close'] > df['lower']
    rsi_limit = rsi < 50
    df.loc[condition1 & rsi_limit, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition_cover = (df['close'] > df['median']) & (df['close'].shift(1) <= df['median'].shift(1))  # K线上穿中轨
    rsi_limit = rsi < 20  # 判断 j值的历史百分位低于30%为超卖，可以做多
    df.loc[rsi_limit, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # # 合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1,
                                                           skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']

    # ===删除无关变量
    df.drop(['std', 'signal_long', 'signal_short'], axis=1, inplace=True)
    # df.drop(['std', 'signal_long', 'signal_short','m','kdj_exceed'], axis=1, inplace=True)
    return df


def signal_double_bolling_rsi_para_list(n_list=range(20, 1000+20, 20), m_list=range(1, 30, 1)):
    """
        :param m_list:
        :param n_list:
        :param bias_pct_list:
        :param stoploss_pct_list:
        :return:
        """
    """
     产生布林 策略的参数范围
     :param m_list:
     :param n_list:
     :return:
     """
    print("参数个数:", len(n_list) * len(m_list))

    para_list = []

    for n in n_list:
        for m in m_list:
            para = [n, m]
            para_list.append(para)

    return para_list
