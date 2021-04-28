import numpy as np

# 布林+bias策略自适应参数1
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

    condition1 = lower2 < median1
    condition2 = lower2.shift(1) >= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # 找出做多平仓信号
    condition1 = df['close'] < median1  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= median1.shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # 找出做空信号
    condition1 = upper2 > median1
    condition2 = upper2.shift(1) <= median1.shift(1)
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # 找出做空平仓信号
    condition1 = df['close'] > median1  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= median1.shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

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

def signal_double_bolling_mod1_para_list(m_list=range(200, 500, 20), n_list=range(10, 200, 2)):
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