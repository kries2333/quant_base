import math
from datetime import datetime, timedelta
from QARealTrade import Signals
import pandas as pd

# 币种面值对照表
coin_value_table = {
    "BTC-USDT": 0.01,
    "EOS-USDT": 10,
    "ETH-USDT": 0.1,
    "ltc-usdt": 1,
    "bch-usdt": 0.1,
    "xrp-usdt": 100,
    "etc-usdt": 10,
    "bsv-usdt": 1,
    "trx-usdt": 1000}

def calculate_signal(symbol_info, symbol_config, symbol_candle_data):
    # 输出变量
    symbol_signal = {}

    # 逐个遍历交易对
    for symbol in symbol_config.keys():
        df = symbol_candle_data[symbol].copy()  # 最新数据
        now_pos = symbol_info.at[symbol, '持仓方向']  # 当前持仓方向
        avg_price = symbol_info.at[symbol, '持仓均价']  # 当前持仓均价

        # 需要计算的目标仓位
        target_pos = None

        # 根据策略计算出目标交易信号。
        if not df.empty:  # 当原始数据不为空的时候
            target_pos = getattr(Signals, symbol_config[symbol]['strategy_name'])(df, now_pos, avg_price, symbol_config[symbol]['para'])
        symbol_info.at[symbol, '目标仓位'] = target_pos  # 这行代码似乎可以删除

        # 根据目标仓位和实际仓位，计算实际操作，"1": "开多"，"2": "开空"，"3": "平多"， "4": "平空"
        if now_pos == 1 and target_pos == 0:  # 平多
            symbol_signal[symbol] = [3]
        elif now_pos == -1 and target_pos == 0:  # 平空
            symbol_signal[symbol] = [4]
        elif now_pos == 0 and target_pos == 1:  # 开多
            symbol_signal[symbol] = [1]
        elif now_pos == 0 and target_pos == -1:  # 开空
            symbol_signal[symbol] = [2]
        elif now_pos == 1 and target_pos == -1:  # 平多，开空
            symbol_signal[symbol] = [3, 2]
        elif now_pos == -1 and target_pos == 1:  # 平空，开多
            symbol_signal[symbol] = [4, 1]

        symbol_info.at[symbol, '信号时间'] = datetime.now()  # 计算产生信号的时间
    symbol_signal[symbol] = [1]
    return symbol_signal


# ===计算实际开仓张数
def cal_order_size(symbol, symbol_info, leverage, volatility_ratio=0.98):
    """
    根据实际持仓以及杠杆数，计算实际开仓张数
    :param symbol:
    :param symbol_info:
    :param leverage:
    :param volatility_ratio:
    :return:
    """
    # 当账户目前有持仓的时候，必定是要平仓，所以直接返回持仓量即可
    hold_amount = symbol_info.at[symbol, "持仓量"]
    if pd.notna(hold_amount):  # 不为空
        return hold_amount

    # 当账户没有持仓时，是开仓
    price = float(symbol_info.at[symbol, "信号价格"])
    coin_value = coin_value_table[symbol]
    e = float(symbol_info.loc[symbol, "账户权益"])
    # 不超过账户最大杠杆
    l = min(float(leverage), float(symbol_info.at[symbol, "最大杠杆"]))
    size = math.floor(e * l * volatility_ratio / (price * coin_value))
    return max(size, 1)  # 防止出现size为情形0，设置最小下单量为1

# ===为了达到成交的目的，计算实际委托价格会向上或者向下浮动一定比例默认为0.02
def cal_order_price(price, order_type, ratio=0.02):
    if order_type in [1, 4]:
        return price * (1 + ratio)
    elif order_type in [2, 3]:
        return price * (1 - ratio)