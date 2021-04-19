import pandas as pd
import numpy as np


# =====简单布林策略
# 策略
def signal_simple_bolling(df, para=[200, 2, 0.3]):
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
    m = para[1]
    x = para[2] / 100

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']


    # ===计算信号
    # 找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多
    df.loc[condition1 & condition2, 'privce_long'] = df['open'].shift(-1)

    # 找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    df.loc[condition1 & condition2, 'privce_long'] = 0

    # 找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空
    df.loc[condition1 & condition2, 'privce_short'] = df['open'].shift(-1)

    # 找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    df.loc[condition1 & condition2, 'privce_short'] = 0

    df['privce_short'].fillna(method='ffill',inplace=True)
    df['privce_long'].fillna(method='ffill',inplace=True)
    df['long_pos']=df['signal_long']
    df['short_pos']=df['signal_short']
    df['long_pos'].fillna(method='ffill',inplace=True)
    df['short_pos'].fillna(method='ffill',inplace=True)

    condition1 = ((df['long_pos'] == 1) & (df['long_pos'].shift(1) == 1)) & (
                (df['close'].shift(1) - df['privce_long']).abs() / df['privce_long'] >= x)
    df.loc[condition1, 'signal_long'] = 0

    condition1 = (df['short_pos'] == -1) & (df['short_pos'].shift(1) == -1) & (
                (df['close'].shift(1) - df['privce_short']).abs() / df['privce_short'] >= x)
    df.loc[condition1, 'signal_short'] = 0

    # 合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']

    # ===删除无关变量
    # df.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short'], axis=1, inplace=True)
    df.drop(['std', 'signal_long', 'signal_short'], axis=1, inplace=True)

    return df

# 策略参数组合
def signal_simple_bolling_para_list(m_list=range(20, 1000+20, 20), n_list=[i / 10 for i in list(np.arange(3, 50+2, 2))],
                                    x_list=[i / 10 for i in list(np.arange(50, 600, 5))]):
    """
    产生布林 策略的参数范围
    :param m_list:
    :param n_list:
    :return:
    """
    print('参数遍历范围：')
    print('m_list', list(m_list))
    print('n_list', list(n_list))
    print('x_list', x_list)

    para_list = []

    for m in m_list:
        for n in n_list:
            for x in x_list:
                para = [m, n, x]
                para_list.append(para)

    return para_list

# 修改简单布林
def signal_kries(df, para=[200, 2, 0.05, -0.05]):
    """
        针对原始布林策略进行修改。
        bias = close / 均线 - 1
        当开仓的时候，如果bias过大，即价格离均线过远，那么就先不开仓。等价格和均线距离小于bias_pct之后，才按照原计划开仓
        由于波动过大，在中线平仓之前，本金已经亏损巨大，为了保证本金的安全增加固定止损条件
        :param df:
        :param para: n,m,bias_pct,stoploss_pct
        :return:
        """

    # ===策略参数
    n = int(para[0])
    m = float(para[1])
    bias_pct = float(para[2])
    stoploss_pct = float(para[3])
    leverage_rate = 2

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']
    # 计算bias
    df['bias'] = df['close'] / df['median'] - 1

    # ===计算原始布林策略信号
    # 找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ===将long和short合并为signal
    df['signal_short'].fillna(method='ffill', inplace=True)
    df['signal_long'].fillna(method='ffill', inplace=True)
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1)
    df['signal'].fillna(value=0, inplace=True)
    df['raw_signal'] = df['signal']

    # ===根据bias，修改开仓时间
    df['temp'] = df['signal']

    # 将原始信号做多时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == 1)
    condition2 = (df['bias'] > bias_pct)
    df.loc[condition1 & condition2, 'temp'] = None

    # 将原始信号做空时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == -1)
    condition2 = (df['bias'] < -1 * bias_pct)
    df.loc[condition1 & condition2, 'temp'] = None

    # 原始信号刚开仓，并且大于阀值，将信号设置为0
    condition1 = (df['signal'] != df['signal'].shift(1))
    condition2 = (df['temp'].isnull())
    df.loc[condition1 & condition2, 'temp'] = 0

    # 使用之前的信号补全原始信号
    df['temp'].fillna(method='ffill', inplace=True)
    df['signal'] = df['temp']

    # 止损代码开始
    # 计算仓位
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(value=0, inplace=True)  # 将初始行数的pos补全为0

    # 计算开仓买入价
    df.loc[df['pos'] != df['pos'].shift(1), 'open_price'] = df['open']
    df['open_price'] = np.where(df['pos'] == 0.0, np.NaN, df['open_price'])
    df['open_price'].fillna(method='ffill', inplace=True)

    # 计算开仓后收益
    df['profit'] = np.where(df['pos'] != 0.0, (df['close'] / df['open_price'] - 1) * df['pos'] * leverage_rate, np.NaN)

    # 计算止损信号
    condition1 = df['pos'] != 0.0
    condition2 = df['profit'] < stoploss_pct
    df['stoploss_sig'] = np.where(condition1 & condition2, 1, np.NaN)
    df.loc[df['pos'] == 0.0, 'stoploss_sig'] = 0
    df['stoploss_sig'].fillna(method='ffill', inplace=True)

    # 根据止损信号，重新计算开平仓信号
    condition1 = df['signal'] != 0.0
    condition2 = df['stoploss_sig'] == 1
    df['signal'] = np.where(condition1 & condition2, 0, df['signal'])

    # ===将signal中的重复值删除
    temp = df[['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp

    df.drop(['raw_signal', 'std', 'bias', 'temp', 'signal_long', 'signal_short', 'pos', 'open_price', 'profit',
             'stoploss_sig'], axis=1, inplace=True)

    return df

def signal_kries_para_list(m_list=range(10, 1001, 20), n_list=[i / 10 for i in list(np.arange(3, 51, 2))],
                                bias_pct_list=[i / 100 for i in list(np.arange(1, 21, 2))],
                                stoploss_pct_list=[i / 100 for i in list(np.arange(-20, -1, 2))]):
    """
        :param m_list:
        :param n_list:
        :param bias_pct_list:
        :param stoploss_pct_list:
        :return:
        """
    print('参数遍历范围：')
    print('m_list', list(m_list))
    print('n_list', list(n_list))
    print('bias_pct_list', list(bias_pct_list))
    print('stoploss_pct_list', list(stoploss_pct_list))

    para_list = []
    for stoploss_pct in stoploss_pct_list:
        for bias_pct in bias_pct_list:
            for m in m_list:
                for n in n_list:
                    para = [m, n, bias_pct, stoploss_pct]
                    para_list.append(para)

    return para_list


# =====作者邢不行
# 策略
def signal_xingbuxing(df, para=[200, 2, 0.05]):
    """
    针对原始布林策略进行修改。
    bias = close / 均线 - 1
    当开仓的时候，如果bias过大，即价格离均线过远，那么就先不开仓。等价格和均线距离小于bias_pct之后，才按照原计划开仓
    :param df:
    :param para: n,m,bias_pct
    :return:
    """

    # ===策略参数
    n = int(para[0])
    m = float(para[1])
    bias_pct = float(para[2])

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']
    # 计算bias
    df['bias'] = df['close'] / df['median'] - 1

    # ===计算原始布林策略信号
    # 找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ===将long和short合并为signal
    df['signal_short'].fillna(method='ffill', inplace=True)
    df['signal_long'].fillna(method='ffill', inplace=True)
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1)
    df['signal'].fillna(value=0, inplace=True)
    df['raw_signal'] = df['signal']

    # ===根据bias，修改开仓时间
    df['temp'] = df['signal']

    # 将原始信号做多时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == 1)
    condition2 = (df['bias'] > bias_pct)
    df.loc[condition1 & condition2, 'temp'] = None

    # 将原始信号做空时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == -1)
    condition2 = (df['bias'] < -1 * bias_pct)
    df.loc[condition1 & condition2, 'temp'] = None

    # 原始信号刚开仓，并且大于阀值，将信号设置为0
    condition1 = (df['signal'] != df['signal'].shift(1))
    condition2 = (df['temp'].isnull())
    df.loc[condition1 & condition2, 'temp'] = 0

    # 使用之前的信号补全原始信号
    df['temp'].fillna(method='ffill', inplace=True)
    df['signal'] = df['temp']

    # ===将signal中的重复值删除
    temp = df[['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp

    df.drop(['raw_signal', 'median', 'std', 'upper', 'lower', 'bias', 'temp', 'signal_long', 'signal_short'], axis=1, inplace=True)

    return df


# 策略参数组合
def signal_xingbuxing_para_list(m_list=range(20, 1000+20, 20), n_list=[i / 10 for i in list(np.arange(3, 50+2, 2))],
                                bias_pct_list=[i / 100 for i in list(np.arange(5, 20+2, 2))]):
    """
    :param m_list:
    :param n_list:
    :param bias_pct_list:
    :return:
    """
    print('参数遍历范围：')
    print('m_list', list(m_list))
    print('n_list', list(n_list))
    print('bias_pct_list', list(bias_pct_list))

    para_list = []
    for bias_pct in bias_pct_list:
        for m in m_list:
            for n in n_list:
                para = [m, n, bias_pct]
                para_list.append(para)

    return para_list