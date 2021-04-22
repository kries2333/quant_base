import pandas as pd
import numpy as np

# 布林+bias策略自适应参数1
def signal_adapt_bolling_mod1(df, para=[200, 0.3]):
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
    bias_pct = float(para[1])

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)

    z_score = abs((df['close'] - df['median']) / df['std'])
    m = z_score.rolling(window=n).max().shift(1)

    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']


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

    df.drop(['raw_signal', 'median', 'std', 'upper', 'lower', 'bias', 'temp', 'signal_long', 'signal_short'], axis=1,
            inplace=True)

    return df


def signal_adapt_bolling_mod1_para_list(n_list=range(20, 1000+20, 20), bias_pct_list=[i / 100 for i in list(np.arange(5, 20+2, 2))]):
    """
        :param m_list:
        :param n_list:
        :param bias_pct_list:
        :param stoploss_pct_list:
        :return:
        """
    print('参数遍历范围：')
    print('n_list', list(n_list))
    print('bias_pct_list', list(bias_pct_list))

    para_list = []
    for bias_pct in bias_pct_list:
        for n in n_list:
            para = [n, bias_pct]
            para_list.append(para)

    return para_list

def signal_mean_bolling_reverse_with_delay(df, para=[200, 2, 0.05]):
    """
    针对原始布林策略进行修改。
    bias = close / 均线 - 1
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
    # 计算每根k线收盘价和均线的差值，取绝对数
    df['cha'] = abs(df['close'] - df['median'])
    # 计算平均差
    df['ping_jun_cha'] = df['cha'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['upper'] = df['median'] + m * df['ping_jun_cha']
    df['lower'] = df['median'] - m * df['ping_jun_cha']
    # 计算bias
    df['bias'] = df['close'] / df['median'] - 1

    # ===计算原始布林策略信号
    df['temp'] = None
    df['temp1'] = None
    # 找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多
    df.loc[condition1 & condition2, 'temp1'] = 1

    # 找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    df.loc[condition1 & condition2, 'temp1'] = 0
    df.loc[condition1 & condition2, 'temp'] = 0

    # 找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空
    df.loc[condition1 & condition2, 'temp1'] = -1

    # 找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    df.loc[condition1 & condition2, 'temp1'] = 0
    df.loc[condition1 & condition2, 'temp'] = 0

    # ===将long和short合并为signal
    df['signal_short'].fillna(method='ffill', inplace=True)
    df['signal_long'].fillna(method='ffill', inplace=True)
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1)
    df['signal'].fillna(value=0, inplace=True)
    df['raw_signal'] = df['signal']

    # 新建信号
    condition3 = df['signal'] != df['signal'].shift(1)
    condition4 = df['signal'] == 1
    condition5 = df['bias'] > bias_pct
    df.loc[condition3 & condition4 & condition5, 'temp'] = -2
    condition4 = df['signal'] == -1
    condition5 = df['bias'] < -1 * bias_pct
    df.loc[condition3 & condition4 & condition5, 'temp'] = 2

    # 合并
    df['signal'] = None
    df['temp'].fillna(method='ffill', inplace=True)
    df['temp1'].fillna(method='ffill', inplace=True)
    df['signal'] = df[['temp', 'temp1']].sum(axis=1)
    df['signal'].fillna(method='ffill', inplace=True)
    df['signal'] = df['signal'][df['signal'] != df['signal'].shift(1)]

    df.drop(['raw_signal', 'median', 'ping_jun_cha', 'upper', 'lower', 'bias', 'signal_long', 'signal_short'], axis=1, inplace=True)

    return df

# 策略参数组合
def signal_mean_bolling_reverse_with_delay_para_list(m_list=range(20, 600+20, 20), n_list=[i / 10 for i in list(np.arange(2, 30, 2))],
                                bias_pct_list=[i / 100 for i in list(np.arange(2, 30, 2))]):
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