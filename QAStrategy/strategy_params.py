from datetime import timedelta
from functools import partial
from multiprocessing import Pool, cpu_count
from datetime import datetime
import pandas as pd

# =====回测固定参数
from QAStrategy.Evaluate import equity_curve_for_OKEx_USDT_future_next_open
from QAStrategy.Position import position_for_OKEx_future
from QAStrategy.Statistics import return_drawdown_ratio
import QAStrategy.Signals
import QAStrategy.Signals_mod1
import QAStrategy.Signals_bias

tag = '20210417'  # 本次回测标记
description = '回测数据基于币安usdt现货的分钟数据'

leverage_rate = 2
slippage = 1 / 1000  # 滑点 ，可以用百分比，也可以用固定值。建议币圈用百分比，股票用固定值
c_rate = 5 / 10000  # 手续费，commission fees，默认为万分之5。不同市场手续费的收取方法不同，对结果有影响。比如和股票就不一样。
min_margin_ratio = 1 / 100  # 最低保证金率，低于就会爆仓
symbol_face_value = {'BTC': 0.01, 'EOS': 10, 'ETH': 0.1, 'LTC': 1,  'XRP': 100, 'DOGE': 10}
drop_days = 10  # 币种刚刚上线10天内不交易

lookup = {'Signals': QAStrategy.Signals, "bias": QAStrategy.Signals_bias , "mod1": QAStrategy.Signals_mod1}

# =====批量遍历策略参数
# ===单次循环
def calculate_by_one_loop(para, model_name, df, signal_name, symbol, rule_type):


    _df = df.copy()
    # 计算交易信号
    _df = getattr(lookup.get(model_name), signal_name)(_df, para=para)
    # 计算实际持仓
    _df = position_for_OKEx_future(_df)
    # 币种上线10天之后的日期
    t = _df.iloc[0]['candle_begin_time'] + timedelta(days=drop_days)
    _df = _df[_df['candle_begin_time'] > t]
    # 计算资金曲线
    face_value = symbol_face_value[symbol]
    _df = equity_curve_for_OKEx_USDT_future_next_open(_df, slippage=slippage, c_rate=c_rate,
                                                      leverage_rate=leverage_rate,
                                                      face_value=face_value,
                                                      min_margin_ratio=min_margin_ratio)

    # 保存策略收益
    rtn = pd.DataFrame()
    rtn.loc[0, 'para'] = str(para)
    r = _df.iloc[-1]['equity_curve']
    rtn.loc[0, '累计净值'] = r  # 最终收益
    rtn.loc[0, '年化收益'], rtn.loc[0, '最大回撤'], rtn.loc[0, '年化收益回撤比'] = return_drawdown_ratio(_df)
    print(signal_name, symbol, rule_type, para, '策略收益：', r)
    return rtn

def straegy_start(model_name, signal_name):
    for symbol in ['DOGE']:
        for rule_type in ['4H', '2H', '1H', '30T', '15T']:
            print(signal_name, symbol, rule_type)
            print('开始遍历该策略参数：', signal_name, symbol, rule_type)

            # ===读入数据
            df = pd.read_pickle('../data/database/%s-USDT_5m.pkl' % symbol)
            # 任何原始数据读入都进行一下排序、去重，以防万一
            df.sort_values(by=['candle_begin_time'], inplace=True)
            df.drop_duplicates(subset=['candle_begin_time'], inplace=True)
            df.reset_index(inplace=True, drop=True)

            # =====转换为其他分钟数据
            period_df = df.resample(rule=rule_type, on='candle_begin_time', label='left', closed='left').agg(
                {'open': 'first',
                 'high': 'max',
                 'low': 'min',
                 'close': 'last',
                 'volume': 'sum'
                 })
            period_df.dropna(subset=['open'], inplace=True)  # 去除一天都没有交易的周期
            period_df = period_df[period_df['volume'] > 0]  # 去除成交量为0的交易周期
            period_df.reset_index(inplace=True)
            df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]
            df = df[df['candle_begin_time'] >= pd.to_datetime('2018-01-01')]
            df.reset_index(inplace=True, drop=True)

            # ===获取策略参数组合
            para_list = getattr(lookup.get(model_name), signal_name + '_para_list')()

            # ===并行回测
            start_time = datetime.now()  # 标记开始时间

            # 利用partial指定参数值
            part = partial(calculate_by_one_loop, model_name=model_name, df=df, signal_name=signal_name, symbol=symbol, rule_type=rule_type)

            with Pool(max(cpu_count() - 2, 1)) as pool:
                # 使用并行批量获得data frame的一个列表
                df_list = pool.map(part, para_list)
                print('读入完成, 开始合并', datetime.now() - start_time)
                # 合并为一个大的DataFrame
                para_curve_df = pd.concat(df_list, ignore_index=True)

            # ===输出
            para_curve_df.sort_values(by='年化收益回撤比', ascending=False, inplace=True)
            print(para_curve_df.head(10))

            # ===存储参数数据
            p = '../data/output/para/%s-%s-%s-%s-%s.csv' % (
                signal_name, symbol, leverage_rate, rule_type, tag)
            pd.DataFrame(columns=[description]).to_csv(p, index=False)
            para_curve_df.to_csv(p, index=False, mode='a')

    return True

if __name__ == '__main__':
    signal_name = 'signal_std1_leverage_bolling'
    temp = "mod1"
    straegy_start(temp, signal_name)