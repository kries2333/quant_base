# 布林+bias策略自适应参数1
def signal_adapt_bolling_Reverse(df, para=[200]):
    """
     针对原始布林策略进行修改。
     反向开仓,中线平仓
     当开仓的时候，如果bias过大，即价格离均线过远，那么就先不开仓。等价格和均线距离小于bias_pct之后，才按照原计划开仓
     :param df:
     :param para: n,m,bias_pct
     :return:
     """

    # ===策略参数
    n = int(para[0])

    # ===计算指标
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度

    z_score = abs((df['close'] - df['median']) / df['std'])
    m = z_score.rolling(window=n).max().shift(1)

    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']

    # ===计算信号
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

    # 新建信号
    condition3 = df['signal'] != df['signal'].shift(1)
    condition4 = df['signal'] == 1
    # condition5 = df['bias'] > bias_pct
    df.loc[condition3 & condition4, 'temp'] = -2
    condition4 = df['signal'] == -1
    # condition5 = df['bias'] < -1 * bias_pct
    df.loc[condition3 & condition4, 'temp'] = 2

    # 合并做多做空信号，去除重复信号
    # df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行
    # temp = df[df['signal'].notnull()][['signal']]
    # temp = temp[temp['signal'] != temp['signal'].shift(1)]
    # df['signal'] = temp['signal']
    # 合并
    df['signal'] = None
    df['temp'].fillna(method='ffill', inplace=True)
    df['temp1'].fillna(method='ffill', inplace=True)
    df['signal'] = df[['temp', 'temp1']].sum(axis=1)
    df['signal'].fillna(method='ffill', inplace=True)
    df['signal'] = df['signal'][df['signal'] != df['signal'].shift(1)]

    df.drop(['raw_signal', 'median', 'ping_jun_cha', 'upper', 'lower', 'bias', 'signal_long', 'signal_short'], axis=1, inplace=True)

    return df

def signal_adapt_bolling_Reverse_para_list(n_list=range(20, 1000+20, 20)):
    """
        :param m_list:
        :param n_list:
        :param bias_pct_list:
        :param stoploss_pct_list:
        :return:
        """
    print('参数遍历范围：')
    print('n_list', list(n_list))

    para_list = []
    for n in n_list:
        para = [n]
        para_list.append(para)

    return para_list