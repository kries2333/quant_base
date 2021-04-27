import pandas as pd
from datetime import timedelta

# =====手工设定策略参数
from QAStrategy import Signals_kries
from QAStrategy.Evaluate import equity_curve_for_OKEx_USDT_future_next_open
from QAStrategy.Position import position_for_OKEx_future
from QAStrategy.Statistics import transfer_equity_curve_to_trade, strategy_evaluate

symbol = 'ETH-USDT_5m'
para = [380, 0.09]
signal_name = 'signal_adapt_bolling_bias'
rule_type = '15min'

symbol_face_value = {'BTC': 0.01, 'EOS': 10, 'ETH': 0.1, 'LTC': 1,  'XRP': 100}
c_rate = 5 / 10000  # 手续费，commission fees，默认为万分之5。不同市场手续费的收取方法不同，对结果有影响。比如和股票就不一样。
slippage = 1 / 1000  # 滑点 ，可以用百分比，也可以用固定值。建议币圈用百分比，股票用固定值
leverage_rate = 2
min_margin_ratio = 1 / 100  # 最低保证金率，低于就会爆仓
drop_days = 10  # 币种刚刚上线10天内不交易

if __name__ == "__main__":
    # =====读入数据
    df = pd.read_pickle('../data/database/%s.pkl' % symbol)
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
         'volume': 'sum',
         'quote_volume': 'sum',
         'trade_num': 'sum',
         'taker_buy_base_asset_volume': 'sum',
         'taker_buy_quote_asset_volume': 'sum',
         })
    period_df.dropna(subset=['open'], inplace=True)  # 去除一天都没有交易的周期
    period_df = period_df[period_df['volume'] > 0]  # 去除成交量为0的交易周期
    period_df.reset_index(inplace=True)
    df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'trade_num',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']]
    df = df[df['candle_begin_time'] >= pd.to_datetime('2017-01-01')]
    df.reset_index(inplace=True, drop=True)

    # =====计算交易信号
    df = getattr(Signals_kries, signal_name)(df, para=para)

    # =====计算实际持仓
    df = position_for_OKEx_future(df)

    # =====计算资金曲线
    # 选取相关时间。币种上线10天之后的日期
    t = df.iloc[0]['candle_begin_time'] + timedelta(days=drop_days)
    df = df[df['candle_begin_time'] > t]

    df = df[df['candle_begin_time'] >= pd.to_datetime('2017-01-01')]
    # print(df)
    # exit()

    # 计算资金曲线
    face_value = symbol_face_value[symbol.split('-')[0]]
    df = equity_curve_for_OKEx_USDT_future_next_open(df, slippage=slippage, c_rate=c_rate, leverage_rate=leverage_rate,
                                                     face_value=face_value, min_margin_ratio=min_margin_ratio)
    print(df)
    print('策略最终收益：', df.iloc[-1]['equity_curve'])
    # 输出资金曲线文件
    df_output = df[
        ['candle_begin_time', 'open', 'high', 'low', 'close', 'signal', 'pos', 'quote_volume', 'median', 'upper',
         'lower', 'equity_change', 'equity_curve']]
    # df_output.rename(columns={'median': 'line_median', 'upper': 'line_upper', 'lower': 'line_lower',
    #                           'quote_volume': 'b_bar_quote_volume',
    #                           'equity_curve': 'r_line_equity_curve'}, inplace=True)
    df_output.to_csv('../data/output/equity_curve/%s_%s_%s_%s.csv' % (signal_name, symbol.split('-')[0],
                                                                                rule_type, str(para)), index=False)

    # =====策略评价
    # 计算每笔交易
    trade = transfer_equity_curve_to_trade(df)
    print('逐笔交易：\n', trade)

    # 计算各类统计指标
    r, monthly_return = strategy_evaluate(df, trade)
    print(r)
    print(monthly_return)