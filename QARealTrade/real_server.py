import time
import traceback

from QAAccount.QAAccount import update_symbol_info
from QAOrder.QAOrder_okex import single_threading_place_order
from QARealTrade.Config import *
from QARealTrade.Function import *
import pandas as pd
import logging
from QAMarket.QAMarket import single_threading_get_data, fetch_symbol_history_candle_data
from QARealTrade.Uity import send_dingding_msg, dingding_report_every_loop, sleep_until_run_time
from QAUilt.common import log_debug, log_info

pd.set_option('display.max_rows', 1000)
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
# 设置命令行输出时的列对齐功能
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
                    filename='210423.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    )

# =交易所配置
OKEX_CONFIG = {
    'apiKey': '7a314674-2f50-4621-a023-4c5a77c7f971',
    'secret': '4BED850944D5EC719B2C52CD932489EF',
    'password': 'Tt84521485',
    'timeout': exchange_timeout,
    'rateLimit': 10,
    # 'hostname': 'okex.me',  # 无法fq的时候启用
    'enableRateLimit': False}

# =====配置交易相关参数=====
# 更新需要交易的合约、策略参数、下单量等配置信息
symbol_config = {
    'BTC-USDT': {'leverage': '2',  # 控制实际交易的杠杆倍数，在实际交易中可以自己修改。此处杠杆数，必须小于页面上的最大杠杆数限制
                 'strategy_name': 'real_signal_simple_bolling_bias1',  # 使用的策略的名称
                 'para': [500, 2.0, 0.08]
                 },  # 策略参数

    'ETH-USDT': {'leverage': '2',  # 控制实际交易的杠杆倍数，在实际交易中可以自己修改。此处杠杆数，必须小于页面上的最大杠杆数限制
                 'strategy_name': 'real_signal_simple_bolling_bias1',  # 使用的策略的名称
                 'para': [540, 2.2, 0.08]
                 },  # 策略参数
}

# 合约代码，当更换合约的时候需要手工修改
symbol_instrument_config = {
    'binance': {
        'BTC-USDT': 'BTCUSDT',
        'ETH-USDT': 'ETHUSDT',
    },
    'okex': {
        'BTC-USDT': 'BTC-USDT-SWAP',
        'ETH-USDT': 'ETH-USDT-SWAP',
    },
}

time_interval = '15m'
max_len = 600
long_sleep_time = 10
ex = 'binance'

def start():

    symbol_candle_data = dict()  # 用于存储K线数据

    # 获取的历史数据
    for symbol in symbol_config.keys():
        symbol_candle_data[symbol] = fetch_symbol_history_candle_data(ex, symbol_instrument_config[ex][symbol], time_interval, max_len)

    while True:
        # 初始化symbol_info，在每次循环开始时都初始化
        symbol_info_columns = ['账户权益', '持仓方向', '持仓量', '持仓收益率', '持仓收益', '持仓均价', '当前价格', '最大杠杆']
        symbol_info = pd.DataFrame(index=symbol_config.keys(), columns=symbol_info_columns)  # 转化为dataframe

        # 更新账户信息symbol_info
        symbol_info = update_symbol_info(ex, symbol_info, symbol_config)
        log_debug("symbol_info = {}".format(symbol_info))

        # =获取策略执行时间，并sleep至该时间
        run_time = sleep_until_run_time(time_interval)

        # =并行获取所有币种最近数据
        candle_num = 10
        recent_candle_data = single_threading_get_data(ex, symbol_info, symbol_config, time_interval, run_time, candle_num)

        # 把历史数据与最新数据合并
        df = symbol_candle_data[symbol].append(recent_candle_data[symbol], ignore_index=True)
        df.drop_duplicates(subset=['candle_begin_time_GMT8'], keep='last', inplace=True)
        df.sort_values(by='candle_begin_time_GMT8', inplace=True, ascending=True)  # 排序，理论上这步应该可以省略，加快速度
        df = df.iloc[-max_len:]  # 保持最大K线数量不会超过max_len个
        df.reset_index(drop=True, inplace=True)
        symbol_candle_data[symbol] = df

        # =计算每个币种的交易信号
        symbol_signal = calculate_signal(symbol_info, symbol_config, symbol_candle_data)
        log_info("symbol_signal = {}".format(symbol_signal))

        # 下单
        symbol_order = pd.DataFrame()
        if symbol_signal:
            symbol_order = single_threading_place_order(symbol_info, symbol_config, symbol_signal)  # 单线程下单
            log_info(symbol_order)

            # 更新订单信息，查看是否完全成交
            time.sleep(short_sleep_time)  # 休息一段时间再更新订单信息
            # symbol_order = update_order_info(exchange, symbol_config, symbol_order)
            log_debug("更新下单记录 = {}".format(symbol_order))

        # 重新更新账户信息symbol_info
        time.sleep(long_sleep_time)  # 休息一段时间再更新
        symbol_info = pd.DataFrame(index=symbol_config.keys(), columns=symbol_info_columns)
        symbol_info = update_symbol_info(ex, symbol_info, symbol_config)
        log_debug("symbol_info = {}".format(symbol_info))

        # 发送钉钉消息
        dingding_report_every_loop(symbol_info, symbol_signal, symbol_order, run_time)

        time.sleep(long_sleep_time)

if __name__ == '__main__':
    while True:
        try:
            start()
        except Exception as e:
            print(e)
            traceback.print_exc()
            time.sleep(long_sleep_time)