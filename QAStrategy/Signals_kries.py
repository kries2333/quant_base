import pandas as pd
import numpy as np

def get_EMA(cps, days):
    emas = cps.copy()  # 创造一个和cps一样大小的集合
    for i in range(len(cps)):
        if i == 0:
            emas[i] = cps[i]
        if i > 0:
            emas[i] = ((days - 1) * emas[i - 1] + 2 * cps[i]) / (days + 1)
    return emas

def get_MACD(df,short=12,long=26,M=9):
    a=get_EMA(df,short)
    b=get_EMA(df,long)
    df['diff']=pd.Series(a)-pd.Series(b)
    #print(df['diff'])
    for i in range(len(df)):
        if i==0:
            df.ix[i,'dea']=df.ix[i,'diff']
        if i>0:
            df.ix[i,'dea']=(2*df.ix[i,'diff']+(M-1)*df.ix[i-1,'dea'])/(M+1)
    df['macd']=2*(df['diff']-df['dea'])
    return df

# 布林+bias策略自适应参数1
def signal_adapt_bolling_bias(df, para=[200, 0.3]):
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

    df.drop(['raw_signal', 'temp', 'signal_long', 'signal_short'], axis=1,
            inplace=True)

    return df

def signal_adapt_bolling_bias_para_list(n_list=range(20, 1000+20, 20), bias_pct_list=[i / 100 for i in list(np.arange(5, 20+2, 2))]):
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


def signal_double_bolling(df, para=[20, 120]):
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

    volume = df['volume'].rolling(n1, min_periods=1).mean()

    std1 = df['close'].rolling(n1, min_periods=1).std(ddof=0)
    std2 = df['close'].rolling(n2, min_periods=1).std(ddof=0)

    z_score = abs((df['close'] - median1) / std1)
    m1 = z_score.rolling(window=n1).max().shift(1)

    z_score = abs((df['close'] - median2) / std2)
    m2 = z_score.rolling(window=n2).max().shift(1)

    upper1 = median1 + m1 * std1
    lower1 = median1 - m1 * std1

    df['upper'] = upper1
    df['lower'] = lower1
    df['median'] = median1

    upper2 = median2 + m2 * std2
    lower2 = median2 - m2 * std2

    condition1 = df['close'] > upper1
    condition2 = df['close'].shift(1) <= upper1.shift(1)
    condition3 = df['close'] > upper2
    condition4 = df['close'].shift(1) <= upper2.shift(1)
    df.loc[condition1 & condition2 & condition3 & condition4, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 找出做多平仓信号
    # condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    # condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    condition1 = df['close'] < median1
    condition2 = df['close'].shift(1) >= median1.shift(1)
    condition3 = df['close'] < median2
    condition4 = df['close'].shift(1) >= median2.shift(1)
    df.loc[condition1 & condition2 & condition3 & condition4, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = df['close'] < lower1  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= lower1.shift(1)  # 之前K线的收盘价 >= 下轨
    condition3 = df['close'] > lower2
    condition4 = df['close'].shift(1) <= lower2.shift(1)
    df.loc[condition1 & condition2 & condition3 & condition4, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition1 = df['close'] > median1  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= median1.shift(1)  # 之前K线的收盘价 <= 中轨
    condition3 = df['close'] < median2
    condition4 = df['close'].shift(1) >= median2.shift(1)
    df.loc[condition1 & condition2 & condition3 & condition4, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']

    # ===删除无关变量
    df.drop(['signal_long', 'signal_short'], axis=1, inplace=True)

    return df

def signal_double_bolling_para_list(m_list=range(10, 100, 2), n_list=range(100, 1000+20, 20)):
    print('参数遍历范围：count', len(m_list) * len(n_list))
    print('m_list', list(m_list))
    print('n_list', list(n_list))

    para_list = []
    for m in m_list:
        for n in n_list:
            para = [m, n]
            para_list.append(para)

    return para_list

def signal_double_bolling_mod1(df, para=[200]):
    """
    :param df:
    :param para: n, m
    :return:
    # 双均线：设置快慢中线，当快线上穿中线，开多，当快线下穿中线开空。
    # n1 快线， n2 慢线
    # 布林线策略
    # 布林线中轨：n天收盘价的移动平均线
    # 布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    # 布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    # 当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。
    # 当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。
    """

    # ===策略参数
    rule_type = (df.iloc[1]['candle_begin_time'] - df.iloc[0]['candle_begin_time']).seconds / 60
    interval = str(int(rule_type))
    preset = {'15': 99, '30': 69, '60': 34, '120': 16, '240': 9}
    pre = preset[interval]

    # ==== 策略参数
    n = int(para[0])

    # ==== 计算指标
    # 计算标准差
    df['std'] = df['close'].rolling(n, ).std(ddof=0)  # ddof代表标准差自由度

    # 计算均线
    df['median'] = df['close'].rolling(n, ).mean()

    # 计算 bias
    df['bias'] = abs(df['close'] / df['median'] - 1)
    df['bias_pct'] = df['bias'].rolling(n, ).max().shift()

    # ==== 计算上轨、下轨道
    # 构建自适应子母布林带
    df['m_std'] = abs(df['close'] - df['median']) / df['std']
    df['m_std'] = df['m_std'].rolling(window=pre, ).mean()  # 先对 df['m_std'] 求pre个窗口的平均值
    df['m_std_max'] = df['m_std'].rolling(window=n, ).max()  # 再用n个窗口内df['m_std']的最大值当作母布林带的m
    df['m_std_min'] = df['m_std'].rolling(window=n, ).min()  # 再用n个窗口内df['m_std']的最小值当作子布林带的m

    df['upper'] = df['median'] + df['m_std_max'] * df['std']
    df['lower'] = df['median'] - df['m_std_max'] * df['std']
    df['up'] = df['median'] + df['m_std_min'] * df['std']
    df['dn'] = df['median'] - df['m_std_min'] * df['std']

    # ==== 计算布林带宽度
    df['scope'] = (df['upper'] - df['lower']) / df['median']
    # 用布林带的宽度过滤
    scope_condition = df['scope'] > df['scope'].rolling(n, ).max().shift(1)

    # 做空自适应止盈
    df['lower_std'] = df['lower'].rolling(n, ).std(ddof=0)
    df['lower_mean'] = df['lower'].rolling(n, ).mean()
    df['lower_std_m'] = abs(df['lower'] - df['lower_mean']) / df['lower_std']
    df['lower_std_m_max'] = df['lower_std_m'].rolling(window=n, ).max()
    df['lower_stop'] = df['lower'] - df['lower_std_m_max'] * df['lower_std']

    # ==== 计算策略信号
    # 找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 母布林带上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 母布林带上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    df.loc[scope_condition, 'signal_long'] = None

    # 找出做多平仓信号
    condition1 = df['close'] < df['up']  # 当前K线的收盘价 < 子布林带上轨
    condition2 = df['close'].shift(1) >= df['up'].shift(1)  # 之前K线的收盘价 >= 子布林带上轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 母布林带下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 母布林带下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    df.loc[scope_condition, 'signal_short'] = None

    # 找出做空平仓信号
    condition1 = df['close'] > df['dn']  # 当前K线的收盘价 > 子布林带下轨
    condition2 = df['close'].shift(1) <= df['dn'].shift(1)  # 之前K线的收盘价 <= 子布林带下轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ==== 使用bias
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)
    df['signal'].fillna(method='ffill', inplace=True)

    # ==== 根据bias，修改开仓时间
    df['temp'] = df['signal']

    # 将原始信号做多时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == 1)
    condition2 = (df['bias'] > df['bias_pct'])
    df.loc[condition1 & condition2, 'temp'] = None

    # 将原始信号做空时，当bias大于阀值，设置为空
    condition1 = (df['signal'] == -1)
    condition2 = (df['bias'] > df['bias_pct'])
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


    if interval in ['30', '60', '120', '240']:
        # ==== 做空止盈
        condition1 = df['close'] < df['lower_stop']
        condition2 = df['signal'] != -1
        condition3 = df['close'].shift(1) > df['lower_stop']
        df.loc[condition1 & condition2 & condition3 , 'signal'] = 0

        temp = df[df['signal'].notnull()][['signal']]
        temp = temp[temp['signal'] != temp['signal'].shift(1)]
        df['signal'] = temp['signal']

    return df

def signal_double_bolling_mod1_para_list(m_list=range(10, 1000, 1)):
    print('参数遍历范围：count', len(m_list))
    print('m_list', list(m_list))

    para_list = []
    for m in m_list:
        para = [m]
        para_list.append(para)

    return para_list